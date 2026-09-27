# [M] CVE-2020-1700

## Summary
Severity: Medium
Advisory: CVE-2020-1700
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-07
Source: https://osv.dev/vulnerability/CVE-2020-1700
Type: osv

## Details
A flaw was found in the way the Ceph RGW Beast front-end handles unexpected disconnects. An authenticated attacker can abuse this flaw by making multiple disconnect attempts resulting in a permanent leak of a socket connection by radosgw. This flaw could lead to a denial of service condition by pile up of CLOSE_WAIT sockets, eventually leading to the exhaustion of available resources, preventing legitimate users from connecting to the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00009.html
- https://usn.ubuntu.com/4304-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1700
