# [H] CVE-2018-16949

## Summary
Severity: High
Advisory: CVE-2018-16949
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-16949
Type: osv

## Details
An issue was discovered in OpenAFS before 1.6.23 and 1.8.x before 1.8.2. Several data types used as RPC input variables were implemented as unbounded array types, limited only by the inherent 32-bit length field to 4 GB. An unauthenticated attacker could send, or claim to send, large input values and consume server resources waiting for those inputs, denying service to other valid connections.

## References
- http://www.securityfocus.com/bid/106375
- https://lists.debian.org/debian-lts-announce/2018/09/msg00024.html
- https://www.debian.org/security/2018/dsa-4302
- http://openafs.org/pages/security/OPENAFS-SA-2018-003.txt
