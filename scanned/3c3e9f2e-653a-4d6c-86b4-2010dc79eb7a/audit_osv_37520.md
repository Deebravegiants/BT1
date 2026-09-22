# [M] Heap Buffer Overflow in Hexadecimal Conversion

## Summary
Severity: Medium
Advisory: CVE-2026-31789
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-31789
Type: osv

## Details
Issue summary: Converting an excessively large OCTET STRING value to
a hexadecimal string leads to a heap buffer overflow on 32 bit platforms.

Impact summary: A heap buffer overflow may lead to a crash or possibly
an attacker controlled code execution or other undefined behavior.

If an attacker can supply a crafted X.509 certificate with an excessively
large OCTET STRING value in extensions such as the Subject Key Identifier
(SKID) or Authority Key Identifier (AKID) which are being converted to hex,
the size of the buffer needed for the result is calculated as multiplication
of the input length by 3. On 32 bit platforms, this multiplication may overflow
resulting in the allocation of a smaller buffer and a heap buffer overflow.

Applications and services that print or log contents of untrusted X.509
certificates are vulnerable to this issue. As the certificates would have
to have sizes of over 1 Gigabyte, printing or logging such certificates
is a fairly unlikely operation and only 32 bit platforms are affected,
this issue was assigned Low severity.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31789.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31789
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/364f095b80601db632b0def6a33316967f863bde
- https://github.com/openssl/openssl/commit/7a9087efd769f362ad9c0e30c7baaa6bbfa65ecf
- https://github.com/openssl/openssl/commit/945b935ac66cc7f1a41f1b849c7c25adb5351f49
- https://github.com/openssl/openssl/commit/a24216018e1ede8ff01a4ff5afff7dfbd443e2f9
- https://github.com/openssl/openssl/commit/a91e537d16d74050dbde50bb0dfb1fe9930f0521
