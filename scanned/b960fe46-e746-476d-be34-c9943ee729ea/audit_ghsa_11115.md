# [H] Glances has Incomplete Secrets Redaction: /api/v4/args Endpoint Leaks Password Hash and SNMP Credentials

## Summary
Severity: High
Advisory: GHSA-cvwp-r2g2-j824
CVE: CVE-2026-32609
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-cvwp-r2g2-j824
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

The GHSA-gh4x fix (commit 5d3de60) addressed unauthenticated configuration secrets exposure on the `/api/v4/config` endpoints by introducing `as_dict_secure()` redaction. However, the `/api/v4/args` and `/api/v4/args/{item}` endpoints were not addressed by this fix. These endpoints return the complete command-line arguments namespace via `vars(self.args)`, which includes the password hash (salt + pbkdf2_hmac), SNMP community strings, SNMP authentication keys, and the configuration file path. When Glances runs without `--password` (the default), these endpoints are accessible without any authentication.

## Details

The secrets exposure fix (GHSA-gh4x, commit 5d3de60) modified three config-related endpoints to use `as_dict_secure()` when no password is configured:

```python
# glances/outputs/glances_restful_api.py:1168 (FIXED)
args_json = self.config.as_dict() if self.args.password else self.config.as_dict_secure()
```

However, the `_api_args` and `_api_args_item` endpoints were not part of this fix and still return all arguments without any sanitization:

```python
# glances/outputs/glances_restful_api.py:1222-1237
def _api_args(self):
    try:
        # Get the RAW value of the args dict
        # Use vars to convert namespace to dict
        args_json = vars(self.args)
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cannot get args ({str(e)})")

    return GlancesJSONResponse(args_json)
```

And the item-specific endpoint:

```python
# glances/outputs/glances_restful_api.py:1239-1258
def _api_args_item(self, item: str):
    ...
    args_json = vars(self.args)[item]
    return GlancesJSONResponse(args_json)
```

The `self.args` namespace contains sensitive fields set during initialization in `glances/main.py`:

1. **`password`** (line 806-819): When `--password` is used, this contains the salt + pbkdf2_hmac hash. An attacker can use this for offline brute-force attacks.

2. **`snmp_community`** (line 445): Default `"public"`, but may be set to a secret community string for SNMP monitoring.

3. **`snmp_user`** (line 448): SNMP v3 username, default `"private"`.

4. **`snmp_auth`** (line 450): SNMP v3 authentication key, default `"password"` but typically set to a secret value.

5. **`conf_file`** (line 198): Path to the configuration file, reveals filesystem structure.

6. **`username`** (line 430/800): The Glances authentication username.

Both endpoints are registered on the authenticated router (line 504-505):
```python
f'{base_path}/args': self._api_args,
f'{base_path}/args/{{item}}': self._api_args_item,
```

When `--password` is not set (the default), the router has NO authentication dependency (line 479-480), making these endpoints completely unauthenticated:
```python
if self.args.password:
    router = APIRouter(prefix=self.url_prefix, dependencies=[Depends(self.authentication)])
else:
    router = APIRouter(prefix=self.url_prefix)
```

## PoC

**Scenario 1: No password configured (default deployment)**

```bash
# Start Glances in web server mode (default, no password)
glances -w

# Access all command line arguments without authentication
curl -s http://localhost:61208/api/4/args | python -m json.tool

# Expected output includes sensitive fields:
# "password": "",
# "snmp_community": "public",
# "snmp_user": "private",
# "snmp_auth": "password",
# "username": "glances",
# "conf_file": "/home/user/.config/glances/glances.conf",

# Access specific sensitive argument
curl -s http://localhost:61208/api/4/args/snmp_community
curl -s http://localhost:61208/api/4/args/snmp_auth
```

**Scenario 2: Password configured (authenticated deployment)**

```bash
# Start Glances with password authentication
glances -w --password --username admin

# Authenticate and access args (password hash exposed to authenticated users)
curl -s -u admin:mypassword http://localhost:61208/api/4/args/password
# Returns the salt$pbkdf2_hmac hash which enables offline brute-force
```

## Impact

- **Unauthenticated network reconnaissance:** When Glances runs without `--password` (the common default for internal/trusted networks), anyone who can reach the web server can enumerate SNMP credentials, usernames, file paths, and all runtime configuration.

- **Offline password cracking:** When authentication is enabled, an authenticated user can retrieve the password hash (salt + pbkdf2_hmac) and perform offline brute-force attacks. The hash uses pbkdf2_hmac with SHA-256 and 100,000 iterations (see `glances/password.py:45`), which provides some protection but is still crackable with modern hardware.

- **Lateral movement:** Exposed SNMP community strings and v3 authentication keys can be used to access other network devices monitored by the Glances instance.

- **Supply chain for CORS attack:** Combined with the default CORS misconfiguration (finding 001), these secrets can be stolen cross-origin by a malicious website.

## Recommended Fix

Apply the same redaction pattern used for the `/api/v4/config` endpoints:

```python
# glances/outputs/glances_restful_api.py

_SENSITIVE_ARGS = frozenset({
    'password', 'snmp_community', 'snmp_user', 'snmp_auth',
    'conf_file', 'password_prompt', 'username_used',
})

def _api_args(self):
    try:
        args_json = vars(self.args).copy()
        if not self.args.password:
            for key in _SENSITIVE_ARGS:
                if key in args_json:
                    args_json[key] = "********"
        # Never expose the password hash, even to authenticated users
        if 'password' in args_json and args_json['password']:
            args_json['password'] = "********"
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cannot get args ({str(e)})")
    return GlancesJSONResponse(args_json)

def _api_args_item(self, item: str):
    if item not in self.args:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown argument item {item}")
    try:
        if item in _SENSITIVE_ARGS:
            if not self.args.password:
                return GlancesJSONResponse("********")
            if item == 'password':
                return GlancesJSONResponse("********")
        args_json = vars(self.args)[item]
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cannot get args item ({str(e)})")
    return GlancesJSONResponse(args_json)
```

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-cvwp-r2g2-j824
- https://nvd.nist.gov/vuln/detail/CVE-2026-32609
- https://github.com/nicolargo/glances/commit/ff14eb9780ee10ec018c754754b1c8c7bfb6c44f
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
