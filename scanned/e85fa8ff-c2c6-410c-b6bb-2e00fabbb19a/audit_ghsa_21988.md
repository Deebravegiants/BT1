# [H] Deserialization of Untrusted Data in Magnolia CMS

## Summary
Severity: High
Advisory: GHSA-pwr6-p3fh-grc2
CVE: CVE-2021-46364
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-pwr6-p3fh-grc2
Type: github-advisory

## Affected
- Maven: `info.magnolia:magnolia-core` — affected >=0 <6.2.4

## Details
A vulnerability in the Snake YAML parser of Magnolia CMS v6.2.3 and below allows attackers to execute arbitrary code via a crafted YAML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46364
- https://docs.magnolia-cms.com/product-docs/6.2/Releases/Release-notes-for-Magnolia-CMS-6.2.4.html#_security_advisory
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2021-46364-YAML%20Deserialization-Magnolia%20CMS
