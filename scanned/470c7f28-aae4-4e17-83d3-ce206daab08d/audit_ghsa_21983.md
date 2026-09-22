# [H] Improper Restriction of XML External Entity Reference in Magnolia CMS

## Summary
Severity: High
Advisory: GHSA-3qpg-33wr-533j
CVE: CVE-2021-46365
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-3qpg-33wr-533j
Type: github-advisory

## Affected
- Maven: `info.magnolia:magnolia-core` — affected >=0 <6.2.4

## Details
An issue in the Export function of Magnolia v6.2.3 and below allows attackers to execute arbitrary code via a crafted XLF file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46365
- https://docs.magnolia-cms.com/product-docs/6.2/Releases/Release-notes-for-Magnolia-CMS-6.2.4.html#_security_advisory
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2021-46365-Unsafe%20XML%20Parsing-Magnolia%20CMS
