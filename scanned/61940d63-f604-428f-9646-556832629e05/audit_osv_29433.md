# [M] Use of Out-of-range Pointer Offset in Mongoose Web Server library

## Summary
Severity: Medium
Advisory: CVE-2024-42383
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-42383
Type: osv

## Details
Use of Out-of-range Pointer Offset vulnerability in Cesanta Mongoose Web Server v7.14 allows to write a NULL byte value beyond the memory space dedicated for the hostname field.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42383.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42383
- https://www.nozominetworks.com/labs/vulnerability-advisories-cve-2024-42383
- https://github.com/cesanta/mongoose
