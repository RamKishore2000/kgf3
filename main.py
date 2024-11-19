import webbrowser
import razorpay
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy import platform

# Razorpay API Keys (Replace with your actual keys)
RAZORPAY_KEY_ID = 'rzp_test_hf2afT5lk394ug'
RAZORPAY_KEY_SECRET = 'bSTTNZLyxYZXdNzb2aRUHLvT'

class Kishore(MDApp):

    def build(self):
        layout = BoxLayout(orientation="vertical", padding=50, spacing=10)

        # Add label to display info
        self.label = Label(text="Enter amount to pay", font_size=24)
        layout.add_widget(self.label)

        # Add text field for amount input
        self.amount_input = MDTextField(
            hint_text="Amount in INR",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            input_filter='float'  # Only numeric input
        )
        layout.add_widget(self.amount_input)

        # Add Pay Now button
        self.pay_button = MDRaisedButton(
            text="Pay Now",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        self.pay_button.bind(on_release=self.start_payment)
        layout.add_widget(self.pay_button)

        return layout

    def start_payment(self, instance):
        # Get the amount entered by the user
        amount_in_inr_str = self.amount_input.text

        # Check if the amount is valid (non-empty and a valid number)
        if not amount_in_inr_str:
            self.label.text = "Please enter a valid amount."
            return
        
        try:
            amount_in_inr = float(amount_in_inr_str)
            if amount_in_inr <= 0:
                self.label.text = "Please enter a positive amount."
                return
        except ValueError:
            self.label.text = "Invalid amount. Please enter a number."
            return

        # Create Razorpay Order
        order_id = self.create_razorpay_order(amount_in_inr)
        
        if order_id:
            # Open Razorpay Checkout modal
            self.open_razorpay_checkout(order_id, amount_in_inr)
        else:
            self.label.text = "Error creating Razorpay order."

    def create_razorpay_order(self, amount_in_inr):
        """Create an order on Razorpay"""
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        amount_in_paise = int(amount_in_inr * 100)  # Convert INR to paise

        order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": "order_receipt_123",
            "payment_capture": 1
        }

        try:
            order = client.order.create(data=order_data)
            return order['id']
        except razorpay.errors.RazorpayError as e:
            print(f"Error creating Razorpay order: {e}")
            return None

    def open_razorpay_checkout(self, order_id, amount_in_inr):
        """Open Razorpay checkout page"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        </head>
        <body>
            <script type="text/javascript">
                var options = {{
                    "key": "{RAZORPAY_KEY_ID}",
                    "amount": {int(amount_in_inr * 100)},  // Convert to paise (ensure it's an integer)
                    "currency": "INR",
                    "order_id": "{order_id}",
                    "name": "Test Company",
                    "description": "Test Payment",
                    "prefill": {{
                        "email": "anv12@gmail.com",
                        "contact": "9121043483"
                    }},
                    "theme": {{
                        "color": "#F37254"
                    }},
                    "handler": function (response) {{
                        alert("Payment successful! Payment ID: " + response.razorpay_payment_id);
                        window.location.href = 'razorpay://payment-status?payment_id=' + response.razorpay_payment_id;
                    }},
                    "modal": {{
                        "escape": false
                    }},
                    "error": function (response) {{
                        alert("Payment failed! Error: " + response.error.description);
                        window.location.href = 'razorpay://payment-failed?error_message=' + response.error.description;
                    }}
                }};
                var rzp1 = new Razorpay(options);
                rzp1.open();
            </script>
        </body>
        </html>
        """
        
        # Save the HTML content to a file
        with open("razorpay_checkout.html", "w") as file:
            file.write(html_content)

        # Open Razorpay Checkout page in a browser
        webbrowser.open("razorpay_checkout.html")

    def on_payment_success(self, payment_id):
        """Handle successful payment"""
        self.label.text = f"Payment successful! Payment ID: {payment_id}"

    def on_payment_failure(self, error_message):
        """Handle failed payment"""
        self.label.text = f"Payment failed! Error: {error_message}"

    def on_start(self):
        """Handle deep link on app start"""
        if platform == 'android':
            # Android specific code here (using Pyjnius or Kivy Android API)
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = PythonActivity.mActivity.getIntent()
            data = intent.getDataString()
            
            if data:
                if data.startswith("razorpay://payment-status"):
                    payment_id = data.split("=")[-1]
                    self.on_payment_success(payment_id)
                elif data.startswith("razorpay://payment-failed"):
                    error_message = data.split("=")[-1]
                    self.on_payment_failure(error_message)

if __name__ == "__main__":
    Kishore().run()
