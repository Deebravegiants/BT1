# [M] Bonitasoft Runtime Community edition's contains an insecure direct object references vulnerability

## Summary
Severity: Medium
Advisory: GHSA-76v2-48w6-crxr
CVE: CVE-2024-28087
CWE: CWE-284, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-76v2-48w6-crxr
Type: github-advisory

## Affected
- Maven: `org.bonitasoft.engine:bonita-server` — affected >=0 <10.1.0.W11

## Details
In Bonitasoft runtime Community edition, the lack of dynamic permissions causes IDOR vulnerability. Dynamic permissions existed only in Subscription edition and have now been restored in Community edition, where they are not custmizable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28087
- https://github.com/bonitasoft/bonita-engine/commit/1b3ac00f0178bfcfe8f01811a249b1893f0b1da1
- https://documentation.bonitasoft.com/bonita/2024.1/release-notes#_fixes_in_bonita_2024_1_u0_2024_04_11
- https://documentation.bonitasoft.com/bonita/latest/release-notes#_fixes_in_bonita_2024_1_2024_04_11
- https://github.com/bonitasoft/bonita-engine
