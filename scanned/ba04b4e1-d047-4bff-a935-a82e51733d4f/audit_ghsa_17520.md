# [H] Crafter Studio Groovy Sandbox Bypass

## Summary
Severity: High
Advisory: GHSA-5644-3vgq-2ph5
CVE: CVE-2025-6384
CWE: CWE-913
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:L/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-06-19
Source: https://github.com/advisories/GHSA-5644-3vgq-2ph5
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-studio` — affected >=4.0.0 <4.3.0

## Details
Improper Control of Dynamically-Managed Code Resources vulnerability in Crafter Studio of CrafterCMS allows authenticated developers to execute OS commands via Groovy Sandbox Bypass.

By inserting malicious Groovy elements, an attacker may bypass Sandbox restrictions and obtain RCE (Remote Code Execution).

This issue affects CrafterCMS: from 4.0.0 through 4.2.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6384
- https://github.com/craftercms/studio/commit/471bbad07cf1f3b420529a020c1409ad57d48a4e
- https://docs.craftercms.org/current/security/advisory.html#cv-2025061901
- https://github.com/craftercms/studio
