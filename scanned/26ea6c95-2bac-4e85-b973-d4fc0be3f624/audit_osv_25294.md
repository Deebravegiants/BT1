# [H] CVE-2023-33204

## Summary
Severity: High
Advisory: CVE-2023-33204
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-33204
Type: osv

## Details
sysstat through 12.7.2 allows a multiplication integer overflow in check_overflow in common.c. NOTE: this issue exists because of an incomplete fix for CVE-2022-39377.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33204.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7UUEKMNDMC6RZTI4O367ZD2YKCOX5THX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NUBFX3UNOSM7KFUIB3J32ASYT5ZRXJQV/
- https://nvd.nist.gov/vuln/detail/CVE-2023-33204
- https://github.com/sysstat/sysstat/pull/360
- https://lists.debian.org/debian-lts-announce/2023/05/msg00026.html
