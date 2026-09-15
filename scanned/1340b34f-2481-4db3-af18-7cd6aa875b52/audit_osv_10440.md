# [H] CVE-2017-15650

## Summary
Severity: High
Advisory: CVE-2017-15650
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/CVE-2017-15650
Type: osv

## Details
musl libc before 1.1.17 has a buffer overflow via crafted DNS replies because dns_parse_callback in network/lookup_name.c does not restrict the number of addresses, and thus an attacker can provide an unexpected number by sending A records in a reply to an AAAA query.

## References
- http://git.musl-libc.org/cgit/musl/commit/?id=45ca5d3fcb6f874bf5ba55d0e9651cef68515395
- http://git.musl-libc.org/cgit/musl/tree/WHATSNEW
- http://openwall.com/lists/oss-security/2017/10/19/5
