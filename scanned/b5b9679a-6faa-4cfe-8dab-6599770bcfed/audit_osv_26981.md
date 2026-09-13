# [M] Marvin Attack vulnerability in SP Math All RSA

## Summary
Severity: Medium
Advisory: CVE-2023-6935
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2023-6935
Type: osv

## Details
wolfSSL SP Math All RSA implementation is vulnerable to the Marvin Attack, new variation of a timing Bleichenbacher style attack, when built with the following options to configure:

--enable-all CFLAGS="-DWOLFSSL_STATIC_RSA"

The define “WOLFSSL_STATIC_RSA” enables static RSA cipher suites, which is not recommended, and has been disabled by default since wolfSSL 3.6.6.  Therefore the default build since 3.6.6, even with "--enable-all", is not vulnerable to the Marvin Attack. The vulnerability is specific to static RSA cipher suites, and expected to be padding-independent.

The vulnerability allows an attacker to decrypt ciphertexts and forge signatures after probing with a large number of test observations. However the server’s private key is not exposed.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6935.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6935
- https://people.redhat.com/~hkario/marvin/
- https://github.com/wolfSSL/wolfssl
