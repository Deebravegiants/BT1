# [H] phpseclib has a CVE-2024-27355 mitigation bypass — OID amplification DoS in ASN1::decodeOID()

## Summary
Severity: High
Advisory: GHSA-3qpq-r242-jqj7
CVE: CVE-2026-44167
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3qpq-r242-jqj7
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=0.1.1 <1.0.29
- Packagist: `phpseclib/phpseclib` — affected >=2.0.0 <2.0.54
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.52

## Details
### Impact
Anyone loading untrusted ASN1 files (eg. X509 certificates, RSA PKCS8 private or public keys, etc)

### Patches
https://github.com/phpseclib/phpseclib/commit/d53d2021bcb9f6a04d5d44ec99e6bbef219a71bc

### Workarounds
No.

### References
https://github.com/phpseclib/phpseclib/commit/d53d2021bcb9f6a04d5d44ec99e6bbef219a71bc

## References
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-3qpq-r242-jqj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44167
- https://github.com/phpseclib/phpseclib/commit/d53d2021bcb9f6a04d5d44ec99e6bbef219a71bc
- https://github.com/phpseclib/phpseclib
