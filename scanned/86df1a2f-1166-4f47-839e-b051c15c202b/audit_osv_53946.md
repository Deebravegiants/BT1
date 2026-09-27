# [H] CVE-2023-33552

## Summary
Severity: High
Advisory: CVE-2023-33552
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-33552
Type: osv

## Details
Heap Buffer Overflow in the erofs_read_one_data function at data.c in erofs-utils v1.6 allows remote attackers to execute arbitrary code via a crafted erofs filesystem image.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FHOIRL6XH5NYR3LYI3KP5DE4SDSQWR7W/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IGGIYW7PHYQM2NPYCJPSPSLULLD2P2PE/
- https://github.com/lometsj/blog_repo/issues/1
