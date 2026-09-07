# [M] XML External Entity Reference in Eclipse Lyo

## Summary
Severity: Medium
Advisory: GHSA-6296-mvgp-27hp
CVE: CVE-2021-41042
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-07-08
Source: https://github.com/advisories/GHSA-6296-mvgp-27hp
Type: github-advisory

## Affected
- Maven: `org.eclipse.lyo:lyo-parent` — affected >=1.0.0 <5.0.0.Final

## Details
In Eclipse Lyo versions 1.0.0 to 4.1.0, a TransformerFactory is initialized with the defaults that do not restrict DTD loading when working with RDF/XML. This allows an attacker to cause an external DTD to be retrieved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41042
- https://github.com/eclipse/lyo/commit/a8b15b7f49ca15e55f6699749c39705d21367c6e
- https://github.com/eclipse/lyo
- https://github.com/eclipse/lyo/releases/tag/v5.0.0
- https://gitlab.eclipse.org/eclipsefdn/emo-team/emo/-/issues/287
