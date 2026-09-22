# [H] CrafterCMS OS Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-j6x3-3jqq-m922
CVE: CVE-2022-40635
CWE: CWE-78, CWE-913
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-j6x3-3jqq-m922
Type: github-advisory

## Affected
- Maven: `org.craftercms:craftercms` — affected >=3.1.0 <3.1.23

## Details
Improper Control of Dynamically-Managed Code Resources vulnerability in Crafter Studio of Crafter CMS allows authenticated developers to execute OS commands via Groovy Sandbox Bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40635
- https://docs.craftercms.org/en/3.1/security/advisory.html#cv-2022051602
- https://github.com/craftercms/craftercms
