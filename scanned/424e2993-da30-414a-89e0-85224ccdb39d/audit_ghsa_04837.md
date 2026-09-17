# [M] Laravel Framework: Temporary Signed URL Path Confusion

## Summary
Severity: Medium
Advisory: GHSA-crmm-hgp2-wgrp
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-crmm-hgp2-wgrp
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=13.0.0 <13.12.0
- Packagist: `laravel/framework` — affected >=0 <12.61.1

## Details
A vulnerability in Laravel's local filesystem driver allows temporary signed URLs to be parsed ambiguously, potentially misrouting requests and bypassing expiration enforcement.

Under certain conditions, a generated temporary signed URL can be interpreted differently by the server than intended at signing time. This may cause requests to resolve to an unintended resource, and can prevent expiration from being enforced, allowing expired URLs to remain valid indefinitely.

### Impact
- Expired temporary URLs may continue to be accepted
- Requests may resolve to a different resource than the one that was signed
- The upload variant may allow writes to reach an unintended destination

## References
- https://github.com/laravel/framework/security/advisories/GHSA-crmm-hgp2-wgrp
- https://github.com/laravel/framework/pull/60137
- https://github.com/laravel/framework/pull/60230
- https://github.com/laravel/framework/pull/60350
- https://github.com/laravel/framework
