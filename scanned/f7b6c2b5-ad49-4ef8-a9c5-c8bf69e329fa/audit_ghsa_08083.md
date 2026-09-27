# [H] Statamic allows Authenticated Control Panel users to escalate privileges via elevated session bypass

## Summary
Severity: High
Advisory: GHSA-rw9x-pxqx-q789
CVE: CVE-2026-27939
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-rw9x-pxqx-q789
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0 <6.4.0

## Details
## Impact

Authenticated Control Panel users may under certain conditions obtain elevated privileges without completing the intended verification step. This can allow access to sensitive operations and, depending on the user’s existing permissions, may lead to privilege escalation.

## Patches
This has been fixed in 6.4.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-rw9x-pxqx-q789
- https://nvd.nist.gov/vuln/detail/CVE-2026-27939
- https://github.com/statamic/cms/commit/8639ef96217eaa682bc42e8a62769cb7c6a85d3a
- https://github.com/statamic/cms
