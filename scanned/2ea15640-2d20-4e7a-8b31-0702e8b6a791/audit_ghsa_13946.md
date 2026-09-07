# [H] openssl-src subject to Invalid pointer dereference in `d2i_PKCS7` functions

## Summary
Severity: High
Advisory: GHSA-29xx-hcv2-c4cp
CVE: CVE-2023-0216
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-29xx-hcv2-c4cp
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.12

## Details
An invalid pointer dereference on read can be triggered when an application tries to load malformed PKCS7 data with the `d2i_PKCS7()`, `d2i_PKCS7_bio()` or `d2i_PKCS7_fp()` functions.

The result of the dereference is an application crash which could lead to a denial of service attack. The TLS implementation in OpenSSL does not call this function however third party applications might call these functions on untrusted data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0216
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=934a04f0e775309cadbef0aa6b9692e1b12a76c6
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2023-0003
- https://rustsec.org/advisories/RUSTSEC-2023-0011.html
- https://security.gentoo.org/glsa/202402-08
- https://www.openssl.org/news/secadv/20230207.txt
