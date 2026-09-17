# [M] Broken access control in Silverpeas

## Summary
Severity: Medium
Advisory: GHSA-vpp3-hpcm-v944
CVE: CVE-2023-47327
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-vpp3-hpcm-v944
Type: github-advisory

## Affected
- Maven: `org.silverpeas.core:silverpeas-core-web` — affected >=0 <6.3.2

## Details
The "Create a Space" feature in Silverpeas Core 6.3.1 is reserved for use by administrators. This function suffers from broken access control, allowing any authenticated user to create a space by navigating to the correct URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47327
- https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2023-47327
- https://github.com/Silverpeas/Silverpeas-Core
- http://silverpeas.com
