# [H] CedarJava has policy injection vulnerability

## Summary
Severity: High
Advisory: GHSA-qmch-v2q9-wg4p
CVE: CVE-2026-55773
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-qmch-v2q9-wg4p
Type: github-advisory

## Affected
- Maven: `com.cedarpolicy:cedar-java` — affected >=0 <2.3.6
- Maven: `com.cedarpolicy:cedar-java` — affected >=3.1.2 <3.4.1
- Maven: `com.cedarpolicy:cedar-java` — affected >=4.0.0 <4.9.0

## Details
### Summary

CedarJava is an open source Java implementation of the Cedar policy language, used for fine-grained authorization decisions. Under certain circumstances, improper input handling could allow policy injection.

### Impact

**Cedar-expression injection via unescaped `toCedarExpr()`**

The `toCedarExpr()` method on Cedar Value types does not escape special characters (`"` or `\`) when converting values to Cedar source code. If an integrator uses `toCedarExpr()` to build policy text at runtime from user-controlled values, an actor could inject arbitrary Cedar expressions. For example, injecting `|| true` into a `permit ... when { ... }` clause could make the permit unconditional, or injecting `&& false` into a `forbid` clause could prevent the `forbid` from triggering.

This issue requires the integrator to use `toCedarExpr()` to build policy text at runtime from user-controlled input.

### Impacted versions: 
< 4.9

### Patches
Addressed in CedarJava version 2.3.6, 3.4.1, and 4.9 and above. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Validate and sanitize all user-supplied input before passing it to `toCedarExpr()`. Avoid building policy text at runtime from user-controlled values.

### References
If you have any questions or comments about this advisory, we ask that you contact us directly via email to [cedar-policy-security@lists.cncf.io](mailto:cedar-policy-security@lists.cncf.io). Please do not create a public GitHub issue.

## References
- https://github.com/cedar-policy/cedar-java/security/advisories/GHSA-qmch-v2q9-wg4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-55773
- https://github.com/cedar-policy/cedar-java
