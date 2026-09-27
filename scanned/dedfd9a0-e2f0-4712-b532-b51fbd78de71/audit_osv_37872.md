# [H] Outline has a rate limit bypass that allows brute force of email login OTP

## Summary
Severity: High
Advisory: CVE-2026-33640
Aliases: GHSA-cwhc-53hw-qqx6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33640
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Outline implements an Email OTP login flow for users not associated with an Identity Provider. Starting in version 0.86.0 and prior to version 1.6.0, Outline does not invalidate OTP codes based on amount or frequency of invalid submissions, rather it relies on the rate limiter to restrict attempts. Consequently, identified bypasses in the rate limiter permit unrestricted OTP code submissions within the codes lifetime. This allows attackers to perform brute force attacks which enable account takeover. Version 1.6.0 fixes the issue.

## References
- https://github.com/outline/outline/releases/tag/v1.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33640.json
- https://github.com/outline/outline/security/advisories/GHSA-cwhc-53hw-qqx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33640
