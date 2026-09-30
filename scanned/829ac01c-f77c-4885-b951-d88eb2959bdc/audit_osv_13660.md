# [H] CVE-2018-20743

## Summary
Severity: High
Advisory: CVE-2018-20743
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-25
Source: https://osv.dev/vulnerability/CVE-2018-20743
Type: osv

## Details
murmur in Mumble through 1.2.19 before 2018-08-31 mishandles multiple concurrent requests that are persisted in the database, which allows remote attackers to cause a denial of service (daemon hang or crash) via a message flood.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00058.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00006.html
- https://www.debian.org/security/2019/dsa-4402
- https://bugs.debian.org/919249
- https://github.com/mumble-voip/mumble/issues/3505
- https://github.com/mumble-voip/mumble/pull/3510
- https://github.com/mumble-voip/mumble/pull/3512
