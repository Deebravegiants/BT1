# [H] Possible Heap Buffer Overflow in ASN.1 Multibyte String Conversion

## Summary
Severity: High
Advisory: CVE-2026-7383
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-7383
Type: osv

## Details
Issue summary: A signed integer overflow when sizing the destination
buffer for Unicode output in ASN1_mbstring_ncopy() can lead to a heap
buffer overflow.

Impact summary: A heap buffer overflow may lead to a crash or possibly
attacker controlled code execution or other undefined behaviour.

In ASN1_mbstring_copy() and ASN1_mbstring_ncopy() the destination
size for Unicode output is computed in a signed int: by left shift
of the input character count for BMPSTRING (UTF-16) and
UNIVERSALSTRING (UTF-32), and by summing per-character byte counts
for UTF8STRING. The calculation overflows when the input reaches
around 2^30 characters. In the worst case (UNIVERSALSTRING at 2^30
characters) the size wraps to zero, OPENSSL_malloc(1) is called, and
the subsequent character copy writes several gigabytes past the
one-byte allocation.

X.509 certificate processing routes through ASN1_STRING_set_by_NID(),
whose DIRSTRING_TYPE mask excludes UNIVERSALSTRING and whose per-NID
size limits cap the input length; no network protocol or
certificate-handling path in OpenSSL exercises the overflow.
Triggering the bug requires an application that calls
ASN1_mbstring_copy() or ASN1_mbstring_ncopy() directly, or registers
a custom string type via ASN1_STRING_TABLE_add(), with
attacker-controlled input on the order of half a gigabyte or more.
For these reasons this issue was assigned Low severity.

The FIPS modules in 4.0, 3.6, 3.5, 3.4 and 3.0 are not affected by
this issue, as the affected code is outside the OpenSSL FIPS module
boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7383
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/4f8d2bddaa2c8e06f9c33390ee1717059a6e4be6
- https://github.com/openssl/openssl/commit/80c15faaf78042bbb8654a0e234c50c381732f74
- https://github.com/openssl/openssl/commit/bd17511070fb39a67bfa19682affb765e706a974
- https://github.com/openssl/openssl/commit/c332adaced43bcbb85f97410597e951c11ec3083
- https://github.com/openssl/openssl/commit/d32350ae8ef7426718f5aa9e383d4b51398ee255
