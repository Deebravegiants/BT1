# [M] Upx: heap-buffer-overflow in packtmt::pack()

## Summary
Severity: Medium
Advisory: CVE-2023-23456
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2023-23456
Type: osv

## Details
A heap-based buffer overflow issue was discovered in UPX in PackTmt::pack() in p_tmt.cpp file. The flow allows an attacker to cause a denial of service (abort) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2024/12/msg00013.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23456.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EL3BVKIGG3SH6I3KPOYQAWCBD4UMPOPI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TGEP3FBNRZXGLIA2B2ICMB32JVMPREFZ/
- https://nvd.nist.gov/vuln/detail/CVE-2023-23456
- https://bugzilla.redhat.com/show_bug.cgi?id=2160381
- https://github.com/upx/upx/issues/632
- https://github.com/upx/upx/commit/510505a85cbe45e51fbd470f1aa8b02157c429d4
- https://github.com/upx/upx
