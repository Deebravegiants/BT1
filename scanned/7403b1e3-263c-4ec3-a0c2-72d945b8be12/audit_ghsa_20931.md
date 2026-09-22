# [H] CrafterCMS Crafter Studio Improperly Controls Dynamically-Managed Code Resources

## Summary
Severity: High
Advisory: GHSA-2jv3-v37p-65w3
CVE: CVE-2022-40634
CWE: CWE-78, CWE-913
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-2jv3-v37p-65w3
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-studio` — affected >=3.1.0 <3.1.23

## Details
Improper Control of Dynamically-Managed Code Resources vulnerability in Crafter Studio of Crafter CMS allows authenticated developers to execute OS commands via FreeMarker SSTI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40634
- https://docs.craftercms.org/en/3.1/security/advisory.html#cv-2022051601
- https://github.com/craftercms/studio
