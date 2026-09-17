# [M] CVE-2020-29485

## Summary
Severity: Medium
Advisory: CVE-2020-29485
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29485
Type: osv

## Details
An issue was discovered in Xen 4.6 through 4.14.x. When acting upon a guest XS_RESET_WATCHES request, not all tracking information is freed. A guest can cause unbounded memory usage in oxenstored. This can lead to a system-wide DoS. Only systems using the Ocaml Xenstored implementation are vulnerable. Systems using the C Xenstored implementation are not vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://www.debian.org/security/2020/dsa-4812
- https://xenbits.xenproject.org/xsa/advisory-330.txt
