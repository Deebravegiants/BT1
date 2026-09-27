# [H] CVE-2018-20102

## Summary
Severity: High
Advisory: CVE-2018-20102
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-12
Source: https://osv.dev/vulnerability/CVE-2018-20102
Type: osv

## Details
An out-of-bounds read in dns_validate_dns_response in dns.c was discovered in HAProxy through 1.8.14. Due to a missing check when validating DNS responses, remote attackers might be able read the 16 bytes corresponding to an AAAA record from the non-initialized part of the buffer, possibly accessing anything that was left on the stack, or even past the end of the 8193-byte buffer, depending on the value of accepted_payload_size.

## References
- http://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=efbbdf72992cd20458259962346044cafd9331c0
- https://lists.debian.org/debian-lts-announce/2022/05/msg00045.html
- http://www.securityfocus.com/bid/106223
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:1436
- https://usn.ubuntu.com/3858-1/
