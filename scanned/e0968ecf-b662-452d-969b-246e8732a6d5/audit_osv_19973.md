# [H] CVE-2021-28831

## Summary
Severity: High
Advisory: CVE-2021-28831
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/CVE-2021-28831
Type: osv

## Details
decompress_gunzip.c in BusyBox through 1.32.1 mishandles the error bit on the huft_build result pointer, with a resultant invalid free or segmentation fault, via malformed gzip data.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3UDQGJRECXFS5EZVDH2OI45FMO436AC4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z7ZIFKPRR32ZYA3WAA2NXFA3QHHOU6FJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZASBW7QRRLY5V2R44MQ4QQM4CZIDHM2U/
- https://lists.debian.org/debian-lts-announce/2021/04/msg00001.html
- https://security.gentoo.org/glsa/202105-09
- https://security.netapp.com/advisory/ntap-20250509-0005/
- https://git.busybox.net/busybox/commit/?id=f25d254dfd4243698c31a4f3153d4ac72aa9e9bd
