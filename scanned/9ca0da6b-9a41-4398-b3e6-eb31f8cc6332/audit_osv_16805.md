# [M] CVE-2019-9824

## Summary
Severity: Medium
Advisory: CVE-2019-9824
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-9824
Type: osv

## Details
tcp_emu in slirp/tcp_subr.c (aka slirp/src/tcp_subr.c) in QEMU 3.0.0 uses uninitialized data in an snprintf call, leading to Information disclosure.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVDHJB2QKXNDU7OFXIHIL5O5VN5QCSZL/
- https://access.redhat.com/errata/RHSA-2019:1650
- https://access.redhat.com/errata/RHSA-2019:2078
- https://access.redhat.com/errata/RHSA-2019:2425
- https://access.redhat.com/errata/RHSA-2019:2553
- https://access.redhat.com/errata/RHSA-2019:3345
- https://lists.gnu.org/archive/html/qemu-devel/2019-03/msg00400.html
