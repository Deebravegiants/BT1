# [M] Jervis Has a JWT Algorithm Confusion Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5pq9-5mpr-jj85
CVE: CVE-2025-68925
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-5pq9-5mpr-jj85
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L244-L249

The code doesn't validate that the JWT header specifies `"alg":"RS256"`.

### Impact

Depending on the broader system, this could allow JWT forgery.

Internally this severity is low since JWT is only intended to interface with GitHub.  External users should consider severity moderate.

### Patches

Jervis patch will explicitly verify the algorithm in the header matches expectations and further verify the JWT structure.

Upgrade to Jervis 2.2.

### Workarounds

External users should consider using an alternate JWT library or upgrade.

### References

- [RFC 7518: JSON Web Algorithms](https://datatracker.ietf.org/doc/html/rfc7518)

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-5pq9-5mpr-jj85
- https://nvd.nist.gov/vuln/detail/CVE-2025-68925
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L244-L249
- http://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
