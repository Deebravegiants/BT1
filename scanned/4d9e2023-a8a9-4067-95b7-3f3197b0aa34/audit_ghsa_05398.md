# [H] Jervis Has a SHA-256 Hex String Padding Bug

## Summary
Severity: High
Advisory: GHSA-67rj-pjg6-pq59
CVE: CVE-2025-68702
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-67rj-pjg6-pq59
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L622-L626

`padLeft(32, '0')` should be `padLeft(64, '0')`. SHA-256 produces 32 bytes = 64 hex characters.

### Impact

* Inconsistent hash lengths when leading bytes are zero
* Comparison failures for hashes with leading zeros
* Potential security issues in hash-based comparisons
* Could cause subtle bugs in systems relying on consistent hash lengths

Severity is considered low for internal uses of this library but if there's any consumer using these methods directly then this is considered high.

### Patches

Upgrade to Jervis 2.2.

### Workarounds

Use an alternate SHA-256 hash function or upgrade.

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-67rj-pjg6-pq59
- https://nvd.nist.gov/vuln/detail/CVE-2025-68702
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L622-L626
- http://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
