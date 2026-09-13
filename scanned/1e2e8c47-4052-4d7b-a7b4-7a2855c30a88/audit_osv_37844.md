# [M] EspoCRM has authenticated SSRF via internal-host validation bypass using alternative IPv4 notation

## Summary
Severity: Medium
Advisory: CVE-2026-33534
Aliases: GHSA-h7gx-8gwv-7g73
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-33534
Type: osv

## Details
EspoCRM is an open source customer relationship management application. Versions 9.3.3 and below have an authenticated Server-Side Request Forgery (SSRF) vulnerability that allows bypassing the internal-host validation logic by using alternative IPv4 representations such as octal notation (e.g., 0177.0.0.1 instead of 127.0.0.1). This is caused by HostCheck::isNotInternalHost() function relying on PHP's filter_var(..., FILTER_VALIDATE_IP), which does not recognize alternative IP formats, causing the validation to fall through to a DNS lookup that returns no records and incorrectly treats the host as safe, however the cURL subsequently normalizes the address and connects to the loopback destination. Through the confirmed /api/v1/Attachment/fromImageUrl endpoint, an authenticated user can force the server to make requests to loopback-only services and store the fetched response as an attachment. This vulnerability is distinct from CVE-2023-46736 (which involved redirect-based SSRF) and may allow access to internal resources reachable from the application runtime. This issue has been fixed in version 9.3.4.

## References
- https://github.com/espocrm/espocrm/releases/tag/9.3.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33534.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-h7gx-8gwv-7g73
- https://nvd.nist.gov/vuln/detail/CVE-2026-33534
