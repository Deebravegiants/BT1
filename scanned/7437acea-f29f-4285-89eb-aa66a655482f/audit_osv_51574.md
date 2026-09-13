# [H] CVE-2021-33646

## Summary
Severity: High
Advisory: CVE-2021-33646
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-10
Source: https://osv.dev/vulnerability/CVE-2021-33646
Type: osv

## Details
The th_read() function doesn’t free a variable t->th_buf.gnu_longname after allocating memory, which may cause a memory leak.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7Q26QDNOJDOFYWMJWEIK5XR62M2FF6IJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7WX5YE66CT7Y5C2HTHXSFDKQWYWYWJ2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OD4HEBSTI22FNYKOKK7W3X6ZQE6FV3XC/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4S4PJRCJLEAWN2EKXGLSOBTL7O57V7NC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5YSHZY753R7XW6CIKJVAWI373WW3YRRJ/
- https://www.openeuler.org/en/security/safety-bulletin/detail.html?id=openEuler-SA-2022-1807
