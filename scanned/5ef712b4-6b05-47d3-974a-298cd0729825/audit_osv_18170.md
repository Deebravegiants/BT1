# [H] CVE-2020-24717

## Summary
Severity: High
Advisory: CVE-2020-24717
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-27
Source: https://osv.dev/vulnerability/CVE-2020-24717
Type: osv

## Details
OpenZFS before 2.0.0-rc1, when used on FreeBSD, misinterprets group permissions as user permissions, as demonstrated by mode 0770 being equivalent to mode 0777.

## References
- https://github.com/openzfs/zfs/commit/716b53d0a14c72bda16c0872565dd1909757e73f
- https://github.com/openzfs/zfs/compare/zfs-0.8.4...zfs-2.0.0-rc1
- https://jira.ixsystems.com/browse/NAS-107270
- https://reviews.freebsd.org/D26107
