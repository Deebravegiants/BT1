# [H] CVE-2016-10746

## Summary
Severity: High
Advisory: CVE-2016-10746
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-18
Source: https://osv.dev/vulnerability/CVE-2016-10746
Type: osv

## Details
libvirt-domain.c in libvirt before 1.3.1 supports virDomainGetTime API calls by guest agents with an RO connection, even though an RW connection was supposed to be required, a different vulnerability than CVE-2019-3886.

## References
- https://lists.debian.org/debian-lts-announce/2019/04/msg00032.html
- https://github.com/libvirt/libvirt/commit/506e9d6c2d4baaf580d489fff0690c0ff2ff588f
- https://github.com/libvirt/libvirt/compare/11288f5...8fd6867
