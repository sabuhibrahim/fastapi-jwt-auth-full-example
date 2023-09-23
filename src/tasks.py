from src.schemas import MailTaskSchema


def user_mail_event(payload: MailTaskSchema):
    # Send mail to user here
    # Now printing only token
    # Token is used for Vefify endpoind
    print(f"[ Mail Schecma ]: {payload}")
