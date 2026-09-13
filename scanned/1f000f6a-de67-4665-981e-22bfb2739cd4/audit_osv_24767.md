# [H] CVE-2023-26257

## Summary
Severity: High
Advisory: CVE-2023-26257
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-27
Source: https://osv.dev/vulnerability/CVE-2023-26257
Type: osv

## Details
An issue was discovered in the Connected Vehicle Systems Alliance (COVESA; formerly GENIVI) dlt-daemon through 2.18.8. Dynamic memory is not released after it is allocated in dlt-control-common.c.

## References
- https://github.com/COVESA/dlt-daemon/pull/441/commits/b6149e203f919c899fefc702a17fbb78bdec3700
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26257.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26257
- https://github.com/COVESA/dlt-daemon/issues/440
- https://lists.debian.org/debian-lts-announce/2024/06/msg00021.html
