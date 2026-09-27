# [H] Blocklist Bypass possible via ECDSA Signature Malleability

## Summary
Severity: High
Advisory: GHSA-69x3-g4r3-p962
CVE: CVE-2026-25793
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-69x3-g4r3-p962
Type: github-advisory

## Affected
- Go: `github.com/slackhq/nebula` — affected >=1.7.0 <1.10.3

## Details
### Impact

When using P256 certificates (which is not the default configuration), it is possible to evade a blocklist entry created against the fingerprint of a certificate by using ECDSA Signature Malleability to use a copy of the certificate with a different fingerprint.

In order for this to affect a user or network, all of the following must be true:
* `CURVE_P256` certificates are being used
* There are one or more entries on the blocklist
* The certificates for those entries are signed by a trusted CA and not expired
* An attacker has a copy of the private key, and corresponding certificate, for one of those blocklist entries

### Patches

See attached

### Workarounds

If full copies of each certificate on the existing blocklist are available, it is possible to compute their opposite-chirality signature, and then the appropriate second fingerprint to list in the blocklist.

Rotating out all CAs that have signed hosts on the blocklist will also prevent exploitation of this vulnerability.

## References
- https://github.com/slackhq/nebula/security/advisories/GHSA-69x3-g4r3-p962
- https://nvd.nist.gov/vuln/detail/CVE-2026-25793
- https://github.com/slackhq/nebula/commit/f573e8a26695278f9d71587390fbfe0d0933aa21
- https://github.com/slackhq/nebula
