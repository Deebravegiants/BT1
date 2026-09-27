# [C] CVE-2021-33643

## Summary
Severity: Critical
Advisory: CVE-2021-33643
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-08-10
Source: https://osv.dev/vulnerability/CVE-2021-33643
Type: osv

## Details
An attacker who submits a crafted tar file with size in header struct being 0 may be able to trigger an calling of malloc(0) for a variable gnu_longlink, causing an out-of-bounds read.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4S4PJRCJLEAWN2EKXGLSOBTL7O57V7NC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5YSHZY753R7XW6CIKJVAWI373WW3YRRJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7Q26QDNOJDOFYWMJWEIK5XR62M2FF6IJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7WX5YE66CT7Y5C2HTHXSFDKQWYWYWJ2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OD4HEBSTI22FNYKOKK7W3X6ZQE6FV3XC/
- https://www.openeuler.org/en/security/safety-bulletin/detail.html?id=openEuler-SA-2022-1807
