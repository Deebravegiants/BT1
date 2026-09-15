# [M] CVE-2026-41034

## Summary
Severity: Medium
Advisory: CVE-2026-41034
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-41034
Type: osv

## Details
ONLYOFFICE DocumentServer before 9.3.0 has an untrusted pointer dereference in XLS processing/conversion (via pictFmla.cbBufInCtlStm and other vectors), leading to an information leak and ASLR bypass.

## References
- https://github.com/ONLYOFFICE/DocumentServer/blob/master/CHANGELOG.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41034
