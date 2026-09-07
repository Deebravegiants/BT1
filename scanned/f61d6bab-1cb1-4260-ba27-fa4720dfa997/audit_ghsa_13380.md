# [C] CasaOS Gateway vulnerable to incorrect identification of source IP addresses

## Summary
Severity: Critical
Advisory: GHSA-vjh7-5r6x-xh6g
CVE: CVE-2023-37265
CWE: CWE-306, CWE-348
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-17
Source: https://github.com/advisories/GHSA-vjh7-5r6x-xh6g
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS-Gateway` — affected >=0 <0.4.4

## Details
### Impact

Unauthenticated attackers can execute arbitrary commands as `root` on CasaOS instances.

### Patches

The problem was addressed by improving the detection of client IP addresses in 391dd7f. This patch is part of CasaOS 0.4.4.

### Workarounds

Users should upgrade to CasaOS 0.4.4. If they can't, they should temporarily restrict access to CasaOS to untrusted users, for instance by not exposing it publicly. 

### References

- 391dd7f
- https://www.sonarsource.com/blog/security-vulnerabilities-in-casaos/

## References
- https://github.com/IceWhaleTech/CasaOS-Gateway/security/advisories/GHSA-vjh7-5r6x-xh6g
- https://nvd.nist.gov/vuln/detail/CVE-2023-37265
- https://github.com/IceWhaleTech/CasaOS-Gateway/commit/391dd7f0f239020c46bf057cfa25f82031fc15f7
- https://github.com/IceWhaleTech/CasaOS-Gateway
- https://pkg.go.dev/vuln/GO-2023-1932
- https://www.sonarsource.com/blog/security-vulnerabilities-in-casaos
