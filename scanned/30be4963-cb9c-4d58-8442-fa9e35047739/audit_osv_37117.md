# [M] Misskey lacks proper authorization checks and input validation

## Summary
Severity: Medium
Advisory: CVE-2026-28431
Aliases: GHSA-r33c-qg3g-v9cr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-28431
Type: osv

## Details
Misskey is an open source, federated social media platform. All Misskey servers running versions 8.45.0 and later, but prior to 2026.3.1, contain a vulnerability that allows bad actors access to data that they ordinarily wouldn't be able to access due to insufficient permission checks and proper input validation. This vulnerability occurs regardless of whether federation is enabled or not. This vulnerability could lead to a significant data breach. This vulnerability is fixed in 2026.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28431.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-r33c-qg3g-v9cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-28431
