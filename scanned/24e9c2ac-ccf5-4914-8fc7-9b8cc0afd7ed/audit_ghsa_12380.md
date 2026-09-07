# [H] Missing access control in Silverpeas

## Summary
Severity: High
Advisory: GHSA-cwh6-hm53-6w2m
CVE: CVE-2023-47323
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-cwh6-hm53-6w2m
Type: github-advisory

## Affected
- Maven: `org.silverpeas.core:silverpeas-core-api` — affected >=0 <6.3.2
- Maven: `org.silverpeas.core:silverpeas-core-web` — affected >=0 <6.3.2

## Details
The notification/messaging feature of Silverpeas Core 6.3.1 does not enforce access control on the ID parameter. This allows an attacker to read all messages sent between other users; including those sent only to administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47323
- https://github.com/Silverpeas/Silverpeas-Core/commit/6383746372d408eeefa73e17ef95608ddd2c7fba
- https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2023-47323
- https://github.com/Silverpeas/Silverpeas-Core
- http://silverpeas.com
