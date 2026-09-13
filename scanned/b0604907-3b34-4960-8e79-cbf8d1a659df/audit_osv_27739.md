# [M] CVE-2024-25385

## Summary
Severity: Medium
Advisory: CVE-2024-25385
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-25385
Type: osv

## Details
An issue in flvmeta v.1.2.2 allows a local attacker to cause a denial of service via the flvmeta/src/flv.c:375:21 function in flv_close.

## References
- https://github.com/hanxuer/crashes/blob/main/flvmeta/01/readme.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25385.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25385
- https://github.com/noirotm/flvmeta/issues/23
