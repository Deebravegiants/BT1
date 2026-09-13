# [H] Phpseclib needs guardrails on large binaryfield integers

## Summary
Severity: High
Advisory: GHSA-2f25-pfq3-c7h8
CVE: CVE-2023-49316
CWE: CWE-400, CWE-834
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-2f25-pfq3-c7h8
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.34

## Details
### Impact
Anyone loading untrusted ASN1 files (eg. X509 certificates, RSA PKCS8 private or public keys, etc)

### Patches
https://github.com/phpseclib/phpseclib/commit/964d78101a70305df33f442f5490f0adb3b7e77f

### Workarounds
No.

### References
https://github.com/phpseclib/phpseclib/commit/964d78101a70305df33f442f5490f0adb3b7e77f
https://www.usenix.org/system/files/usenixsecurity25-shi-bing.pdf

## References
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-2f25-pfq3-c7h8
- https://nvd.nist.gov/vuln/detail/CVE-2023-49316
- https://github.com/phpseclib/phpseclib/commit/964d78101a70305df33f442f5490f0adb3b7e77f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpseclib/phpseclib/CVE-2023-49316.yaml
- https://github.com/phpseclib/phpseclib
- https://github.com/phpseclib/phpseclib/releases/tag/3.0.34
