# [M] CVE-2026-42371

## Summary
Severity: Medium
Advisory: CVE-2026-42371
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/CVE-2026-42371
Type: osv

## Details
uriparser before 1.0.1 has numeric truncation in text range comparison, if an application accepts URIs with a length in gigabytes.

## References
- http://www.openwall.com/lists/oss-security/2026/04/27/2
- https://uriparser.github.io
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42371
- https://github.com/uriparser/uriparser/pull/298
