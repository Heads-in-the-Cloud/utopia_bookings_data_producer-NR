from faker import Faker
from faker_airtravel import AirTravelProvider
import random
import requests

FLIGHTS_URL = "http://localhost:8081/api/flights"
BOOKINGS_URL = "http://localhost:8083/api/bookings"
AUTH_URL = "http://localhost:8084/api"
USER_URL = "http://localhost:8082/api/users"

fake = Faker()
fake.add_provider(AirTravelProvider)


def add_bookings(token):
    for i in range(227):
        x = requests.post(f"{BOOKINGS_URL}/add", headers={"Authorization": token})
        if x.status_code != 201:
            print(x.text)
            break


def add_flight_bookings(token):
    flights = requests.get(
        f"{FLIGHTS_URL}/all", headers={"Authorization": token}
    ).json()
    bookings = requests.get(
        f"{BOOKINGS_URL}/all", headers={"Authorization": token}
    ).json()
    for i in range(len(flights)):
        if i >= len(bookings):
            break
        flight_id = flights[i]["id"]
        booking_id = bookings[i]["id"]
        fb = {"flightId": flight_id, "bookingId": booking_id}
        x = requests.post(
            f"{BOOKINGS_URL}/flightbookings/add",
            headers={"Authorization": token},
            json=fb,
        )
        if x.status_code != 201:
            print(x.text)
            break


def add_booking_payment(token):
    bookings = requests.get(
        f"{BOOKINGS_URL}/all", headers={"Authorization": token}
    ).json()
    for i in range(len(bookings)):
        booking_id = bookings[i]["id"]
        payment = {
            "bookingId": booking_id,
            "stripeId": fake.credit_card_number(),
            "refunded": random.choice([True, False]),
        }
        x = requests.post(
            f"{BOOKINGS_URL}/payment/add",
            headers={"Authorization": token},
            json=payment,
        )
        if x.status_code != 201:
            print(x.text)
            break


def add_passengers(token):
    bookings = requests.get(
        f"{BOOKINGS_URL}/all", headers={"Authorization": token}
    ).json()
    for i in range(len(bookings)):
        booking_id = bookings[i]["id"]
        passenger = {
            "bookingId": booking_id,
            "givenName": fake.first_name(),
            "familyName": fake.last_name(),
            "gender": random.choice(["Male", "Female", "Other"]),
            "address": fake.street_address() + " " + fake.postcode(),
            "dob": fake.date_of_birth(minimum_age=12).strftime("%Y-%m-%d"),
        }
        x = requests.post(
            f"{BOOKINGS_URL}/passenger/add",
            headers={"Authorization": token},
            json=passenger,
        )
        if x.status_code != 201:
            print(x.text)
            break


def add_booking_guest(booking_id):
    guest = {
        "bookingId": booking_id,
        "contactEmail": fake.email(),
        "contactPhone": fake.phone_number(),
    }
    return guest


def add_booking_user(booking_id, user_id):
    ua = {"bookingId": booking_id, "userId": user_id}
    return ua


def add_booking_agent(booking_id, user_id):
    ua = {"bookingId": booking_id, "agentId": user_id}
    return ua


def add_booking_users(token):
    headers = {"Authorization": token}
    users = requests.get(f"{USER_URL}/all", headers=headers).json()
    bookings = requests.get(f"{BOOKINGS_URL}/all", headers=headers).json()
    for _ in range(len(users)):
        user_id = random.choice(users)["id"]
        booking_id = random.choice(bookings)["id"]
        route = random.choice(["agent", "guest", "user"])
        u = dict()
        if route == "guest":
            u = add_booking_guest(booking_id)
        elif route == "user":
            u = add_booking_user(booking_id, user_id)
        else:
            u = add_booking_agent(booking_id, user_id)
        x = requests.post(
            f"{BOOKINGS_URL}/booking{route}/add",
            headers=headers,
            json=u,
        )
        if x.status_code != 201:
            print(x.status_code)
            print(x.text)
            break


if __name__ == "__main__":
    up = {"username": "admin", "password": "1234"}
    res = requests.post(f"{AUTH_URL}/login", data=up)
    token = "Bearer " + res.json()["access_token"]
    print(token)
    # add_bookings(token)
    add_booking_users(token)
