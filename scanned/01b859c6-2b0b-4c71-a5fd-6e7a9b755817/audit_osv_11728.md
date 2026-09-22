# [M] CVE-2017-9434

## Summary
Severity: Medium
Advisory: CVE-2017-9434
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9434
Type: osv

## Details
Crypto++ (aka cryptopp) through 5.6.5 contains an out-of-bounds read vulnerability in zinflate.cpp in the Inflator filter.

## References
- http://www.securityfocus.com/bid/99007
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7IL5A6465IEPW5GAWGXB2ENJPFYVWTJM/
- http://openwall.com/lists/oss-security/2017/06/06/2
- https://github.com/weidai11/cryptopp/commit/07dbcc3d9644b18e05c1776db2a57fe04d780965
- https://github.com/weidai11/cryptopp/issues/414
