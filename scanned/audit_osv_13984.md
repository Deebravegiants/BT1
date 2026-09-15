# [H] CVE-2018-6003

## Summary
Severity: High
Advisory: CVE-2018-6003
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-22
Source: https://osv.dev/vulnerability/CVE-2018-6003
Type: osv

## Details
An issue was discovered in the _asn1_decode_simple_ber function in decoding.c in GNU Libtasn1 before 4.13. Unlimited recursion in the BER decoder leads to stack exhaustion and DoS.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://gitlab.com/gnutls/libtasn1/commit/946565d8eb05fbf7970ea366e817581bb5a90910
- https://www.debian.org/security/2018/dsa-4106
- https://bugzilla.redhat.com/show_bug.cgi?id=1535926
- https://bugzilla.suse.com/show_bug.cgi?id=1076832
- http://git.savannah.nongnu.org/cgit/libtasn1.git/commit/?id=c593ae84cfcde8fea45787e53950e0ac71e9ca97
