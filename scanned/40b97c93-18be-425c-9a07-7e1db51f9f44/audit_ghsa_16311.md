# [C] Central Dogma Authentication Bypass Vulnerability via Session Leakage

## Summary
Severity: Critical
Advisory: GHSA-34q3-p352-c7q8
CVE: CVE-2024-1143
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-34q3-p352-c7q8
Type: github-advisory

## Affected
- Maven: `com.linecorp.centraldogma:centraldogma-server` — affected >=0 <0.64.1

## Details
### Vulnerability Overview
A vulnerability has been identified in Central Dogma versions prior to 0.64.1, allowing for the leakage of user sessions and subsequent authentication bypass. The issue stems from a Cross-Site Scripting (XSS) attack vector that targets the RelayState of Security Assertion Markup Language (SAML).

### Impact
Successful exploitation of this vulnerability enables malicious actors to leak user sessions, leading to the compromise of authentication mechanisms. This, in turn, can facilitate unauthorized access to sensitive resources.

### Patches
This vulnerability is addressed and resolved in Central Dogma version 0.64.1 Users are strongly encouraged to upgrade to this version or later to mitigate the risk associated with the authentication bypass.

### Workarounds
No viable workarounds are currently available for this vulnerability. It is recommended to apply the provided patch promptly.

### References
- [OASIS SAML v2.0 Errata 05](https://docs.oasis-open.org/security/saml/v2.0/errata05/os/saml-v2.0-errata05-os.html#__RefHeading__8196_1983180497)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html#xss-defense-philosophy)

## References
- https://github.com/line/centraldogma/security/advisories/GHSA-34q3-p352-c7q8
- https://nvd.nist.gov/vuln/detail/CVE-2024-1143
- https://github.com/line/centraldogma/commit/8edcf913b88101aff70008156b0881850e005783
- https://github.com/line/centraldogma
