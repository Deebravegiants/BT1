# [M] CVE-2022-2928

## Summary
Severity: Medium
Advisory: CVE-2022-2928
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/CVE-2022-2928
Type: osv

## Details
In ISC DHCP 4.4.0 -> 4.4.3, ISC DHCP 4.1-ESV-R1 -> 4.1-ESV-R16-P1, when the function option_code_hash_lookup() is called from add_option(), it increases the option's refcount field. However, there is not a corresponding call to option_dereference() to decrement the refcount field. The function add_option() is only used in server responses to lease query packets. Each lease query response calls this function for several options, so eventually, the reference counters could overflow and cause the server to abort.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2SARIK7KZ7MGQIWDRWZFAOSQSPXY4GOU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QQXYCIWUDILRCNBAIMVFCSGXBRKEPB4K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T6IBFH4MRRNJQVWEKILQ6I6CXWW766FX/
- https://kb.isc.org/docs/cve-2022-2928
- https://lists.debian.org/debian-lts-announce/2022/10/msg00015.html
- https://security.gentoo.org/glsa/202305-22
