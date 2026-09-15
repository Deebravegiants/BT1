# [M] CVE-2022-2929

## Summary
Severity: Medium
Advisory: CVE-2022-2929
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/CVE-2022-2929
Type: osv

## Details
In ISC DHCP 1.0 -> 4.4.3, ISC DHCP 4.1-ESV-R1 -> 4.1-ESV-R16-P1 a system with access to a DHCP server, sending DHCP packets crafted to include fqdn labels longer than 63 bytes, could eventually cause the server to run out of memory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2SARIK7KZ7MGQIWDRWZFAOSQSPXY4GOU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QQXYCIWUDILRCNBAIMVFCSGXBRKEPB4K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T6IBFH4MRRNJQVWEKILQ6I6CXWW766FX/
- https://kb.isc.org/docs/cve-2022-2929
- https://lists.debian.org/debian-lts-announce/2022/10/msg00015.html
- https://security.gentoo.org/glsa/202305-22
