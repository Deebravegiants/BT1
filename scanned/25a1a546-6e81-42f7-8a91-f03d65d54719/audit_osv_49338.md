# [H] CVE-2019-10222

## Summary
Severity: High
Advisory: CVE-2019-10222
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-08
Source: https://osv.dev/vulnerability/CVE-2019-10222
Type: osv

## Details
A flaw was found in the Ceph RGW configuration with Beast as the front end handling client requests. An unauthenticated attacker could crash the Ceph RGW server by sending valid HTTP headers and terminating the connection, resulting in a remote denial of service for Ceph RGW clients.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://tracker.ceph.com/issues/40018
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10222
