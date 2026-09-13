# [M] Book Stack v23.10.2 - LFR via Blind SSRF

## Summary
Severity: Medium
Advisory: CVE-2023-6199
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-11-20
Source: https://osv.dev/vulnerability/CVE-2023-6199
Type: osv

## Details
Book Stack version 23.10.2 allows filtering local files on the server. This is possible because the application is vulnerable to SSRF.

## References
- https://fluidattacks.com/advisories/imagination/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6199.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6199
- https://www.bookstackapp.com/blog/bookstack-release-v23-10-3/
