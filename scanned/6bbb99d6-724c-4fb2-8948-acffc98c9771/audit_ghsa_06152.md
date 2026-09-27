# [C] New API: User List API Leaks Root User Access Token Leading to Privilege Escalation

## Summary
Severity: Critical
Advisory: GHSA-6x2c-phff-wx57
CVE: CVE-2026-64859
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-6x2c-phff-wx57
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <1.0.0-rc.7

## Details
## Vulnerability Information

- **Product**: new-api
- **Affected versions**: versions before `v1.0.0-rc.7` that serialize `User.AccessToken` as `access_token`; the issue was confirmed in `v0.12.14`
- **Patched version**: `v1.0.0-rc.7`
- **Fixed commit**: `0936e2504655a5cbf7bc3c388f6d3e2bb24916d3`
- **Type**: Information Disclosure / Privilege Escalation

## Description

In affected versions of new-api, the admin user list and user lookup APIs can return the `access_token` field for users, including the root user. An authenticated admin user can call endpoints such as `GET /api/user/` to retrieve user records. Because access tokens function as bearer credentials for API authentication, leaking the root user's access token allows an admin user to authenticate as root and access root-only endpoints such as system configuration APIs.

This bypasses the intended role boundary between admin users and the root user and can result in privilege escalation to full system control.

## Root Cause

The `User.AccessToken` field was serialized as `json:"access_token"` in affected versions. User management APIs returned `User` model objects directly after omitting only the password field from database queries, so JSON serialization could include `access_token` in API responses.

Affected code patterns include user list, user search, and user detail paths that use `Omit("password")` without preventing `access_token` from being serialized.

## Impact

- An authenticated admin user may obtain the root user's access token.
- The attacker may impersonate the root user and access root-only APIs.
- The attacker may modify system settings, payment settings, OAuth/SMTP-related configuration, and other sensitive platform options.
- Access tokens for other users may also be exposed, enabling user impersonation.

## Remediation

Upgrade to `v1.0.0-rc.7` or later. The fix changes `User.AccessToken` to use `json:"-"`, preventing the field from being serialized in API responses.

Operators should also rotate any root or user access tokens that may have been exposed before upgrading, especially if untrusted admin users had access to user management APIs.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-6x2c-phff-wx57
- https://github.com/QuantumNous/new-api/pull/4929
- https://github.com/QuantumNous/new-api/commit/0936e2504655a5cbf7bc3c388f6d3e2bb24916d3
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.7
