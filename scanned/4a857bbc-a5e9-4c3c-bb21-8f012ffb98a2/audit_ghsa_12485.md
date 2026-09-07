# [H] github.com/ecies/go vulnerable to possible private key restoration

## Summary
Severity: High
Advisory: GHSA-8j98-cjfr-qx3h
CVE: CVE-2023-49292
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-8j98-cjfr-qx3h
Type: github-advisory

## Affected
- Go: `github.com/ecies/go/v2` — affected >=0 <2.0.8

## Details
### Impact
If functions `Encapsulate()`, `Decapsulate()` and `ECDH()` could be called by an attacker, he could recover any private key that he interacts with.

### Patches
Patched in v2.0.8

### Workarounds
You could manually check public key by calling `IsOnCurve()` function from secp256k1 libraries.

### References
https://github.com/ashutosh1206/Crypton/blob/master/Diffie-Hellman-Key-Exchange/Attack-Invalid-Curve-Point/README.md

## References
- https://github.com/ecies/go/security/advisories/GHSA-8j98-cjfr-qx3h
- https://nvd.nist.gov/vuln/detail/CVE-2023-49292
- https://github.com/ecies/go/commit/c6e775163866d6ea5233eb8ec8530a9122101ebd
- https://github.com/ashutosh1206/Crypton/blob/master/Diffie-Hellman-Key-Exchange/Attack-Invalid-Curve-Point/README.md
- https://github.com/ecies/go
- https://github.com/ecies/go/releases/tag/v2.0.8
