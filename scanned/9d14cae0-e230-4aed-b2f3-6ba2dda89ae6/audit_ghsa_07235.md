# [H] Cedar-Java has policy injection, type confusion, and incorrect equality comparison vulnerabilities

## Summary
Severity: High
Advisory: GHSA-4r9r-4425-74p7
CVE: CVE-2026-55771
CWE: CWE-697, CWE-843, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-4r9r-4425-74p7
Type: github-advisory

## Affected
- Maven: `com.cedarpolicy:cedar-java` — affected >=0 <2.3.6
- Maven: `com.cedarpolicy:cedar-java` — affected >=3.1.2 <3.4.1
- Maven: `com.cedarpolicy:cedar-java` — affected >=4.0.0 <4.9.0

## Details
### Summary

CedarJava is an open source Java implementation of the Cedar policy language, used for fine-grained authorization decisions. Under certain circumstances, it could lead to incorrect equality comparisons.

### Impact

**`EntityIdentifier.equals()` has inverted null/self branches**

The `EntityIdentifier.equals()` method has inverted logic for null and self-reference checks, returning true for null comparisons and false for self-comparisons. This does not affect Cedar authorization decisions (computed in Rust from JSON), but could affect integrators who perform their own equality checks on entity identifiers.

### Impacted versions: 
< 4.9

### Patches
It has been addressed in CedarJava version 4.9 and above. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Avoid relying on `EntityIdentifier.equals()` for security-sensitive comparisons until upgraded to version `4.9`.

### References
If you have any questions or comments about this advisory, Cedar asks that you contact us directly via email to [cedar-policy-security@lists.cncf.io](mailto:cedar-policy-security@lists.cncf.io). Please do not create a public GitHub issue.

## References
- https://github.com/cedar-policy/cedar-java/security/advisories/GHSA-4r9r-4425-74p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-55771
- https://github.com/cedar-policy/cedar-java
