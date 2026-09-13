# [M] CVE-2023-33461

## Summary
Severity: Medium
Advisory: CVE-2023-33461
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-33461
Type: osv

## Details
iniparser v4.1 is vulnerable to NULL Pointer Dereference in function iniparser_getlongint which misses check NULL for function iniparser_getstring's return.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33461.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ASV7SEDHGCP63GYAFEW3CTTVQDZM5RIK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BQAIP5AURSTWIQOOP7G4CXYJ5IIGPY3Q/
- https://nvd.nist.gov/vuln/detail/CVE-2023-33461
- https://github.com/ndevilla/iniparser/issues/144
