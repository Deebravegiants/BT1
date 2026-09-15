# [H] openssl-src subject to NULL dereference validating DSA public key

## Summary
Severity: High
Advisory: GHSA-vxrh-cpg7-8vjr
CVE: CVE-2023-0217
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-vxrh-cpg7-8vjr
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.12

## Details
An invalid pointer dereference on read can be triggered when an application tries to check a malformed DSA public key by the `EVP_PKEY_public_check()` function. This will most likely lead to an application crash. This function can be called on public keys supplied from untrusted sources which could allow an attacker to cause a denial of service attack.

The TLS implementation in OpenSSL does not call this function but applications might call the function if there are additional security requirements imposed by standards such as FIPS 140-3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0217
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=23985bac83fd50c8e29431009302b5442f985096
- https://rustsec.org/advisories/RUSTSEC-2023-0012.html
- https://security.gentoo.org/glsa/202402-08
- https://www.openssl.org/news/secadv/20230207.txt
