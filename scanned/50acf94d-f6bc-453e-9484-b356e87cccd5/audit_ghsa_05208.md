# [M] Shopware: Privilege escalation: non-admin user with user:create ACL can create admin accounts

## Summary
Severity: Medium
Advisory: GHSA-v39m-97p8-gqg7
CVE: CVE-2026-48010
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-v39m-97p8-gqg7
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.18
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.18

## Details
`UserController::upsertUser()` writes user data in `SYSTEM_SCOPE` and does not filter the `admin` field. A non-admin API user with `user:create` or `user:update` ACL permission can set `admin: true` on new or existing users, escalating to full admin access.

## The Problem

In `src/Core/Framework/Api/Controller/UserController.php`, line 210-234:

```php
public function upsertUser(?string $userId, Request $request, Context $context, ResponseFactoryInterface $factory): Response
{
    $data = $request->request->all(); // raw request data, no field filtering
    // ...
    $events = $context->scope(Context::SYSTEM_SCOPE, fn (Context $context) =>
        $this->userRepository->upsert([$data], $context)
    );
}
```

`SYSTEM_SCOPE` bypasses `AclWriteValidator` entirely (line 52 of `AclWriteValidator::preValidate()` returns early for `SYSTEM_SCOPE`). The `admin` boolean field is accepted without restriction.

Compare with `IntegrationController::upsertIntegration()` in the same codebase, which correctly checks:

```php
if ((!$source instanceof AdminApiSource)
    || (!$source->isAdmin()
    && isset($data['admin']))
) {
    throw new PermissionDeniedException();
}
```

`UserController` is missing this exact check.

## Impact

Any API user with the low-privilege `user:create` permission can create accounts with full admin access, or with `user:update` can promote any existing user to admin. This is a direct privilege escalation.

## Suggested Fix

Add the same `isAdmin()` check from `IntegrationController`:

```php
$source = $context->getSource();
if ((!$source instanceof AdminApiSource) || (!$source->isAdmin() && isset($data['admin']))) {
    throw new PermissionDeniedException();
}
```

Best regards,
Keyvan Hardani

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-v39m-97p8-gqg7
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.18
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
