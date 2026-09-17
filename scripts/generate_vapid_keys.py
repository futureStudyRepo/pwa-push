import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


private_key = ec.generate_private_key(ec.SECP256R1())
private_number = private_key.private_numbers().private_value
private_key_bytes = private_number.to_bytes(32, "big")

public_key = private_key.public_key()
public_numbers = public_key.public_numbers()
public_key_bytes = b"\x04" + public_numbers.x.to_bytes(32, "big") + public_numbers.y.to_bytes(32, "big")

pem_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

print("PWA_VAPID_PUBLIC_KEY=" + b64url(public_key_bytes))
print("PWA_VAPID_PRIVATE_KEY=" + b64url(private_key_bytes))
print()
print("PEM reference:")
print(pem_private.decode("utf-8"))
