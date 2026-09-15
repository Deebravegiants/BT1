# [M] phpMyFAQ: Ordinary Authenticated User Can Access Admin-Only API Endpoints Due to Insufficient Authorization Check in phpMyFAQ

## Summary
Severity: Medium
Advisory: GHSA-jrc5-w569-h7h5
CVE: CVE-2026-45009
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-jrc5-w569-h7h5
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=4.1.1 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=4.1.1 <4.1.2

## Details
### Summary

A review of `phpMyFAQ-main` uncovered an authorization issue in the `admin-api` routes.

Several backend endpoints only check whether the caller is logged in. They do not verify that the caller actually has backend or administrative privileges. As a result, a normal frontend user can access API endpoints that are clearly intended for administrative use.

During local reproduction, a regular user account was able to request `/admin/api/index.php/dashboard/versions` and receive a successful response from the backend management API.

This issue does not appear to give direct write access in the affected paths that were confirmed, so it should be treated as a backend information disclosure and privilege boundary failure rather than full admin compromise.

### Details

The access control split is visible in the controller base class:

```php
public function userIsAuthenticated(): void
{
    if (!$this->currentUser->isLoggedIn()) {
        throw new UnauthorizedHttpException('Unauthorized access.');
    }
}

protected function userHasPermission(PermissionType $permissionType): void
{
    // permission-based check
}
```

The problem is that several `Administration\Api` controllers use the weaker check even though the routes sit under the backend API namespace.

For example, `phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/DashboardController.php` exposes:

```php
#[Route(path: 'dashboard/versions', name: 'admin.api.dashboard.versions', methods: ['GET'])]
public function versions(): JsonResponse
{
    $this->userIsAuthenticated();
    ...
}
```

The same pattern appears in other backend-facing controllers, including:

- `LdapController`
- `ElasticsearchController`
- `OpenSearchController`
- `UpdateController`

That matters because these endpoints are not part of the normal frontend feature set. They expose backend operational data such as version checks, upgrade state, LDAP configuration, health checks, and search backend status.

Three examples that stand out from an impact perspective are:

1. `GET /admin/api/index.php/ldap/configuration`

   This can expose LDAP server configuration, mapping settings, group settings, and general authentication-related options. Even with secrets masked, this is still useful internal infrastructure information.

2. `GET /admin/api/index.php/elasticsearch/statistics`

   If Elasticsearch is enabled, this can expose index names and search backend statistics that should normally stay in the admin area.

3. `GET /admin/api/index.php/health-check`

   This is part of the update and maintenance workflow and can reveal operational state that ordinary users should not be able to inspect.

In other words, the issue is not that guests can reach the backend. The issue is that any ordinary authenticated user can cross the frontend/backend privilege boundary.

### PoC

I reproduced this against a local Docker deployment of the project.

First, an unauthenticated request to the backend API is rejected:

```http
GET /admin/api/index.php/dashboard/versions HTTP/1.1
Host: 127.0.0.1
Accept: application/json
```

Response:

```http
HTTP/1.0 401 Unauthorized
Content-Type: application/problem+json

{
  "type": "http://127.0.0.1/problems/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Unauthorized access.",
  "instance": "/dashboard/versions"
}
```

Logged in with a normal frontend account:

- username: `user1`
- password: `User12345!`

After login, the same request was sent with the user session cookie:

```http
GET /admin/api/index.php/dashboard/versions HTTP/1.1
Host: 127.0.0.1
Cookie: PHPSESSID=<regular-user-session>
Accept: application/json
```

Response:

```http
HTTP/1.0 200 OK
Content-Type: application/json

{"success":"Latest version available: phpMyFAQ 4.1.1"}
```

That is enough to show that a non-admin account can call at least one backend management endpoint successfully.

### Impact

The main impact is unauthorized access to backend-only operational information.

Depending on which optional features are enabled in a real deployment, this may let a normal user learn:

- upgrade and version status
- maintenance or health-check information
- LDAP environment details
- Elasticsearch or OpenSearch backend status and statistics
- internal administrative diagnostics

This was rated as **Medium** severity.

It was not categorized as **High** severity because the testing done did not confirm a direct administrative state change through the affected read-oriented endpoints. Still, this is a real privilege separation failure. A frontend account should not be able to query backend admin APIs simply because it has a valid session.

### Remediation

The suggested approach should fix this in two layers.

1. Replace `userIsAuthenticated()` with explicit permission checks on backend endpoints that are intended for administrators only.
2. Review all `Administration\Api` controllers for similar cases and make the access model consistent.
3. Keep backend operational endpoints separated from ordinary user sessions unless there is a strong business reason to expose them.
4. Add regression tests that log in as a low-privileged user and verify that backend routes return `403` or `401` where appropriate.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-jrc5-w569-h7h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45009
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-insufficient-authorization-check-in-admin-api-endpoints
