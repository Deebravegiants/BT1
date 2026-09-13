# [M] CVE-2024-1298

## Summary
Severity: Medium
Advisory: CVE-2024-1298
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-1298
Type: osv

## Details
EDK2 contains a vulnerability when S3 sleep is activated where an Attacker may cause a Division-By-Zero due to a UNIT32 overflow via local access. A successful exploit of this vulnerability may lead to a loss of Availability.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F7NUL7NSZQ76A5OKDUCODQNY7WSX4SST/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VIMEZWDKEIQKU7NMHKL57DOCITPGEXYN/
- https://security.netapp.com/advisory/ntap-20250306-0002/
- https://github.com/tianocore/edk2/security/advisories/GHSA-chfw-xj8f-6m53
