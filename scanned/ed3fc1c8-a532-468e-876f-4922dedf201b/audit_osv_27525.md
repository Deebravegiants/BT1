# [M] CVE-2024-23301

## Summary
Severity: Medium
Advisory: CVE-2024-23301
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2024-23301
Type: osv

## Details
Relax-and-Recover (aka ReaR) through 2.7 creates a world-readable initrd when using GRUB_RESCUE=y. This allows local attackers to gain access to system secrets otherwise only readable by root.

## References
- https://lists.debian.org/debian-lts-announce/2025/12/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7JIN57LUPBI2GDJOK3PYXNHJTZT3AQTZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UHKMPXJNXEJJE6EVYE5HM7EKEJFQMBN7/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23301.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7JIN57LUPBI2GDJOK3PYXNHJTZT3AQTZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHKMPXJNXEJJE6EVYE5HM7EKEJFQMBN7/
- https://nvd.nist.gov/vuln/detail/CVE-2024-23301
- https://github.com/rear/rear/issues/3122
- https://github.com/rear/rear/pull/3123
- https://lists.debian.org/debian-lts-announce/2024/02/msg00003.html
