# [M] Nimbus JOSE + JWT is vulnerable to DoS attacks when processing deeply nested JSON

## Summary
Severity: Medium
Advisory: GHSA-xwmg-2g98-w7v9
CVE: CVE-2025-53864
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-11
Source: https://github.com/advisories/GHSA-xwmg-2g98-w7v9
Type: github-advisory

## Affected
- Maven: `com.nimbusds:nimbus-jose-jwt` — affected >=9.38-rc1 <10.0.2
- Maven: `com.nimbusds:nimbus-jose-jwt` — affected >=0 <9.37.4

## Details
Connect2id Nimbus JOSE + JWT before 10.0.2 allows a remote attacker to cause a denial of service via a deeply nested JSON object supplied in a JWT claim set, because of uncontrolled recursion. NOTE: this is independent of the Gson 2.11.0 issue because the Connect2id product could have checked the JSON object nesting depth, regardless of what limits (if any) were imposed by Gson.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53864
- https://github.com/google/gson/commit/1039427ff0100293dd3cf967a53a55282c0fef6b
- https://bitbucket.org/connect2id/nimbus-jose-jwt
- https://bitbucket.org/connect2id/nimbus-jose-jwt/commits/f7fb882cc08f027c9ceb874acec3b51c6222861c
- https://bitbucket.org/connect2id/nimbus-jose-jwt/issues/583/stackoverflowerror-due-to-deeply-nested
- https://bitbucket.org/connect2id/nimbus-jose-jwt/issues/593/back-port-cve-2025-53864-fix-to-9x-branch
- https://github.com/google/gson/compare/gson-parent-2.11.0...gson-parent-2.12.0
