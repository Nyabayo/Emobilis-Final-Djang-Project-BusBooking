import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Book

# Utility function to initiate M-Pesa Payment
def initiate_mpesa_payment(booking):
    # Check if phone_number exists in user model
    if not hasattr(booking.user, 'phone_number'):
        raise Exception("User does not have a phone number associated.")

    headers = {
        'Authorization': 'Bearer ' + get_access_token(),
        'Content-Type': 'application/json',
    }

    payload = {
        "Shortcode": settings.MPESA_SHORTCODE,  # Store your shortcode in settings
        "LipaCode": settings.MPESA_LIPA_CODE,
        "Amount": booking.price * booking.nos,  # The total amount to be paid
        "PhoneNumber": booking.user.phone_number,  # Ensure phone_number is stored in user model
        "CallbackURL": settings.MPESA_CALLBACK_URL + "/mpesa/callback/",  # Callback URL for payment status
    }

    # Send the POST request to initiate payment
    try:
        response = requests.post(settings.MPESA_PAYMENT_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        response_data = response.json()

        # Check if the response contains the Payment URL
        if response.status_code == 200 and 'PaymentURL' in response_data:
            return response_data.get('PaymentURL')  # Redirect user to this URL to complete payment
        else:
            error_message = response_data.get('error_message', 'Unknown error')
            raise Exception(f"Failed to initiate M-Pesa payment: {error_message}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except ValueError as e:
        raise Exception(f"Failed to parse response from M-Pesa: {str(e)}")


def get_access_token():
    # Your client credentials for M-Pesa API
    api_key = settings.MPESA_API_KEY
    api_secret = settings.MPESA_API_SECRET
    api_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        # Make request to get the access token
        response = requests.get(api_url, auth=(api_key, api_secret))
        response.raise_for_status()  # Raise an HTTPError for bad responses
        access_token = response.json().get('access_token')

        if not access_token:
            raise Exception("Failed to retrieve access token.")

        return access_token
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed while getting access token: {str(e)}")
    except ValueError as e:
        raise Exception(f"Failed to parse access token response: {str(e)}")

