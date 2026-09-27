# [C] CVE-2025-22952

## Summary
Severity: Critical
Advisory: CVE-2025-22952
Aliases: GHSA-wfxg-v3j4-7qmj, GO-2025-3492
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-22952
Type: osv

## Details
elestio memos v0.23.0 is vulnerable to Server-Side Request Forgery (SSRF) due to insufficient validation of user-supplied URLs, which can be exploited to perform SSRF attacks.

## References
- https://elest.io/open-source/memos
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22952.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22952
- https://github.com/usememos/memos/issues/4413
- https://github.com/usememos/memos/pull/4428
- https://github.com/usememos/memos
