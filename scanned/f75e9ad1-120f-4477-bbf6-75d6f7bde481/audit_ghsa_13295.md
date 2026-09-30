# [C] CasaOS contains weak JWT secrets

## Summary
Severity: Critical
Advisory: GHSA-m5q5-8mfw-p2hr
CVE: CVE-2023-37266
CWE: CWE-1391, CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-17
Source: https://github.com/advisories/GHSA-m5q5-8mfw-p2hr
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS` — affected >=0 <0.4.4

## Details
### Impact

Unauthenticated attackers can craft arbitrary JWTs and access features that usually require authentication and execute arbitrary commands as `root` on CasaOS instances.

### Patches

The problem was addressed by improving the validation of JWTs in 705bf1f. This patch is part of CasaOS 0.4.4.

### Workarounds

Users should upgrade to CasaOS 0.4.4. If they can't, they should temporarily restrict access to CasaOS to untrusted users, for instance by not exposing it publicly.

### References

- 705bf1f
- https://www.sonarsource.com/blog/security-vulnerabilities-in-casaos/

## References
- https://github.com/IceWhaleTech/CasaOS/security/advisories/GHSA-m5q5-8mfw-p2hr
- https://nvd.nist.gov/vuln/detail/CVE-2023-37266
- https://github.com/IceWhaleTech/CasaOS/commit/705bf1facbffd2ca40b159b0303132b6fdf657ad
- https://github.com/IceWhaleTech/CasaOS
- https://pkg.go.dev/vuln/GO-2023-1931
- https://www.sonarsource.com/blog/security-vulnerabilities-in-casaos
