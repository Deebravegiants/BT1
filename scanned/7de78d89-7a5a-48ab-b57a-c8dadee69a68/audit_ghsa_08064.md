# [M] Crafter CMS has Improper Control of Dynamically-Managed Code Resources

## Summary
Severity: Medium
Advisory: GHSA-gj28-gw7w-3pxc
CVE: CVE-2026-1770
CWE: CWE-913
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:L/VI:H/VA:H/SC:H/SI:H/SA:H/E:U (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-gj28-gw7w-3pxc
Type: github-advisory

## Affected
- Maven: `org.craftercms:craftercms` — affected >=4.0.0 <4.5.0

## Details
Improper Control of Dynamically-Managed Code Resources vulnerability in Crafter Studio of Crafter CMS allows authenticated developers to execute OS commands via Groovy Sandbox Bypass. By inserting malicious Groovy elements, an attacker may bypass sandbox restrictions and obtain RCE (Remote Code Execution).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1770
- https://docs.craftercms.org/current/security/advisory.html#cv-2026020201
- https://github.com/craftercms/craftercms
