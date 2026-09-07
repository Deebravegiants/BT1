# [H] Cross-Site Request Forgery in Magnolia CMS

## Summary
Severity: High
Advisory: GHSA-hxvf-35w8-f5mw
CVE: CVE-2021-46366
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-hxvf-35w8-f5mw
Type: github-advisory

## Affected
- Maven: `info.magnolia:magnolia-core` — affected >=0 <6.2.4

## Details
An issue in the Login page of Magnolia CMS v6.2.3 and below allows attackers to exploit both an Open Redirect vulnerability and Cross-Site Request Forgery (CSRF) in order to brute force and exfiltrate users' credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46366
- https://docs.magnolia-cms.com/product-docs/6.2/Releases/Release-notes-for-Magnolia-CMS-6.2.4.html#_security_advisory
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2021-46366-CSRF%2BOpen%20Redirect-Magnolia%20CMS
