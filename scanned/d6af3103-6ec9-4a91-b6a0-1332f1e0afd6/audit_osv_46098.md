# [M] wolfSSL SP Math All RSA implementation is vulnerable to the Marvin Attack, new variation of a timing...

## Summary
Severity: Medium
Advisory: JLSEC-2026-677
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-677
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
wolfSSL SP Math All RSA implementation is vulnerable to the Marvin Attack, new variation of a timing Bleichenbacher style attack, when built with the following options to configure:

--enable-all CFLAGS="-`DWOLFSSL_STATIC_RSA`"

The define “`WOLFSSL_STATIC_RSA`” enables static RSA cipher suites, which is not recommended, and has been disabled by default since wolfSSL 3.6.6.  Therefore the default build since 3.6.6, even with "--enable-all", is not vulnerable to the Marvin Attack. The vulnerability is specific to static RSA cipher suites, and expected to be padding-independent.

The vulnerability allows an attacker to decrypt ciphertexts and forge signatures after probing with a large number of test observations. However the server’s private key is not exposed.

## References
- https://github.com/advisories/GHSA-r36f-f47x-637q
- https://nvd.nist.gov/vuln/detail/CVE-2023-6935
- https://people.redhat.com/~hkario/marvin
- https://people.redhat.com/~hkario/marvin/
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
