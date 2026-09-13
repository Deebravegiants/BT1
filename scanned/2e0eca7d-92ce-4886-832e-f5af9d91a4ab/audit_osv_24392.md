# [H] CVE-2023-1393

## Summary
Severity: High
Advisory: CVE-2023-1393
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-1393
Type: osv

## Details
A flaw was found in X.Org Server Overlay Window. A Use-After-Free may lead to local privilege escalation. If a client explicitly destroys the compositor overlay window (aka COW), the Xserver would leave a dangling pointer to that window in the CompScreen structure, which will trigger a use-after-free later.

## References
- https://www.openwall.com/lists/oss-security/2023/03/29/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1393.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BPNQYHUI63DB5FHK6EOI3Z4C6YQZGZKI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H3EVO3OQV6T4BSABWZ2TU3PY5TJTEQZ2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MEHSYYFGBN3G4RS2HJXKQ5NBMOAZ5F2F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NOYATGGPMT3COC7ELAJW5TG2PVS3AFR2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PSAAGI5V77FQXIT5PP4URP6BYQVCK5U5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QHJMSMK7G4GPLMKIGKXIOL2RTKU5VFWE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SW2NRC3V53PIBXFPFBVWCOM2MDDILWQS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SWFUDSBSABRHQOX6TIQ5O3SNPFTPFQQP/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1393
- https://security.gentoo.org/glsa/202305-30
- https://gitlab.freedesktop.org/xorg/xserver/-/commit/26ef545b3502f61ca722a7a3373507e88ef64110
