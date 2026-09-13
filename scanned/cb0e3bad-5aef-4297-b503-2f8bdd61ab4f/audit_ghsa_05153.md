# [H] SolidInvoice: IDOR in LiveComponent allows same-company cross-user access to API tokens and notification transport settings

## Summary
Severity: High
Advisory: GHSA-7vfx-4246-jcfh
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-7vfx-4246-jcfh
Type: github-advisory

## Affected
- Packagist: `solidinvoice/solidinvoice` — affected >=0 <2.3.16

## Details
## Summary

Four authorization bypass vulnerabilities in Symfony LiveComponent actions allow any authenticated user within a company to access, modify, or delete other users' API tokens and notification transport settings. The root cause is that LiveComponent actions accept entity IDs without verifying ownership, while the listing methods correctly filter by user.

## Findings

### 1. Cross-User API Token Revocation (MEDIUM)

**File:** `src/UserBundle/Twig/Components/ApiTokens.php`, lines 50-55

The `revoke()` LiveAction accepts any `ApiToken` via `#[LiveArg]` without checking ownership. The `apiTokens()` method correctly filters by user (`getApiTokensForUser($this->security->getUser())`).

```php
#[LiveAction]
public function revoke(#[LiveArg] ApiToken $token): void
{
    $this->apiTokenRepository->revoke($token); // No ownership check
}
```

### 2. Cross-User API Token History Disclosure (MEDIUM)

**File:** `src/UserBundle/Twig/Components/ApiTokenHistory.php`, lines 30-55

The writable `$token` LiveProp performs `$this->apiTokenRepository->find($this->token)` without user verification. Exposes IP addresses, request methods, paths, and user agents from other users' API token usage.

### 3. Cross-User Notification Transport Settings Disclosure (HIGH)

**File:** `src/NotificationBundle/Twig/Components/NotificationIntegrations.php`, lines 48-55

The `integration()` method performs `$this->repository->find($this->setting)` using a writable LiveProp without user check. The `enabledIntegrations()` method correctly filters: `$this->repository->findBy(['user' => $this->getUser()])`.

The `TransportSetting` entity stores notification credentials in a JSON `settings` column, potentially exposing API keys for Slack, Discord, Telegram, or SMS services.

### 4. Cross-User Notification Transport Setting Takeover (HIGH)

**File:** `src/NotificationBundle/Twig/Components/NotificationTransportConfiguration.php`, lines 39-40, 84-101

The writable `$setting` LiveProp accepts any `TransportSetting` entity. The `save()` action overwrites the user field with the current user via `$setting->setUser($user)`, effectively stealing the transport configuration and its stored credentials.

## Root Cause

The application relies on Doctrine's `CompanyFilter` for tenant isolation but has no user-level access controls within a company. LiveComponent actions that resolve entities from client-provided IDs don't verify ownership.

## Suggested Fix

Add user ownership verification in each LiveAction/LiveProp before performing operations:
```php
if ($token->getUser() !== $this->security->getUser()) {
    throw $this->createAccessDeniedException();
}
```

## References
- https://github.com/SolidInvoice/SolidInvoice/security/advisories/GHSA-7vfx-4246-jcfh
- https://github.com/SolidInvoice/SolidInvoice
