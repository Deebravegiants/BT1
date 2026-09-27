# [H] CVE-2017-7869

## Summary
Severity: High
Advisory: CVE-2017-7869
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7869
Type: osv

## Details
GnuTLS before 2017-02-20 has an out-of-bounds write caused by an integer overflow and heap-based buffer overflow related to the cdk_pkt_read function in opencdk/read-packet.c. This issue (which is a subset of the vendor's GNUTLS-SA-2017-3 report) is fixed in 3.5.10.

## References
- http://www.securityfocus.com/bid/97040
- https://access.redhat.com/errata/RHSA-2017:2292
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=420
- https://gitlab.com/gnutls/gnutls/commit/51464af713d71802e3c6d5ac15f1a95132a354fe
- https://www.gnutls.org/security.html
