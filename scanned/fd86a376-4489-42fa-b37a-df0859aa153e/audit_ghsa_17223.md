# [M] Central Dogma's Login Function Has an Open Redirect Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4hr2-xf7w-jf76
CVE: CVE-2025-11222
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-4hr2-xf7w-jf76
Type: github-advisory

## Affected
- Maven: `com.linecorp.centraldogma:centraldogma-server-auth-shiro` — affected >=0 <0.78.0

## Details
### Impact
Successful exploitation of this vulnerability could allow an attacker to craft a malicious link that, when clicked by a victim, redirects them to a phishing website designed to mimic the legitimate Central Dogma login page. This could result in the compromise of user accounts and unauthorized access to the Central Dogma instance.

### Patches
This vulnerability is addressed and resolved in Central Dogma version 0.78.0. The server operators who run Central Dogma server with Shiro authentication are strongly encouraged to upgrade to this version or later to mitigate the risk associated with the open redirect vulnerability.

### Workarounds
Implement `AuthProvider` to overrides `webLoginService()`.

### References
- https://cwe.mitre.org/data/definitions/601.html

## References
- https://github.com/line/centraldogma/security/advisories/GHSA-4hr2-xf7w-jf76
- https://nvd.nist.gov/vuln/detail/CVE-2025-11222
- https://github.com/line/centraldogma/pull/1207
- https://github.com/line/centraldogma/commit/95e7bbd77266493e4ec70b670bd91fa3e3289de0
- https://github.com/line/centraldogma
