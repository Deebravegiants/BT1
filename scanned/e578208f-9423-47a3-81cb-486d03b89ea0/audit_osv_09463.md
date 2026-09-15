# [H] CVE-2016-9939

## Summary
Severity: High
Advisory: CVE-2016-9939
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-9939
Type: osv

## Details
Crypto++ (aka cryptopp and libcrypto++) 5.6.4 contained a bug in its ASN.1 BER decoding routine. The library will allocate a memory block based on the length field of the ASN.1 object. If there is not enough content octets in the ASN.1 object, then the function will fail and the memory block will be zeroed even if its unused. There is a noticeable delay during the wipe for a large allocation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7IL5A6465IEPW5GAWGXB2ENJPFYVWTJM/
- http://www.debian.org/security/2016/dsa-3748
- http://www.securityfocus.com/bid/94854
- http://www.openwall.com/lists/oss-security/2016/12/12/7
