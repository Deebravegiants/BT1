# [H] Botan Vulnerable to Denial of Service Due to Overly Large Elliptic Curve Parameters

## Summary
Severity: High
Advisory: CVE-2024-34703
Aliases: GHSA-w4g2-7m2h-7xj7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-30
Source: https://osv.dev/vulnerability/CVE-2024-34703
Type: osv

## Details
Botan is a C++ cryptography library. X.509 certificates can identify elliptic curves using either an object identifier or using explicit encoding of the parameters. Prior to versions 3.3.0 and 2.19.4, an attacker could present an ECDSA X.509 certificate using explicit encoding where the parameters are very large. The proof of concept used a 16Kbit prime for this purpose. When parsing, the parameter is checked to be prime, causing excessive computation. This was patched in 2.19.4 and 3.3.0 to allow the prime parameter of the elliptic curve to be at most 521 bits. No known workarounds are available. Note that support for explicit encoding of elliptic curve parameters is deprecated in Botan.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34703.json
- https://github.com/randombit/botan/security/advisories/GHSA-w4g2-7m2h-7xj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-34703
- https://github.com/randombit/botan/commit/08c404b23740babee1f6aa51b54e966029aadee4
- https://github.com/randombit/botan/commit/94e9154c143aa5264da6254a6a1be5bc66ee2b5a
