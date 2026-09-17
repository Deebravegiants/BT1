# [H] Jervis Has Weak Random for Timing Attack Mitigation

## Summary
Severity: High
Advisory: GHSA-c9q6-g3hr-8gww
CVE: CVE-2025-68704
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-c9q6-g3hr-8gww
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L593-L594

Uses `java.util.Random()` which is not cryptographically secure.

### Impact

If an attacker can predict the random delays, they may still be able to perform timing attacks.

### Patches

Jervis will use `SecureRandom` for timing randomization.

Upgrade to Jervis 2.2.

### Workarounds

None

### References

- [OWASP Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-c9q6-g3hr-8gww
- https://nvd.nist.gov/vuln/detail/CVE-2025-68704
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L593-L594
- http://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
