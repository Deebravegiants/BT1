# [H] XML Injection in Crafter CMS Crafter Studio 3.0.1

## Summary
Severity: High
Advisory: GHSA-5hr6-vc97-qxxh
CVE: CVE-2017-15685
CWE: CWE-91
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-5hr6-vc97-qxxh
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-studio` — affected >=0 <3.0.2

## Details
Crafter CMS Crafter Studio 3.0.1 is affected by: XML External Entity (XXE). An unauthenticated attacker is able to create a site with specially crafted XML that allows the retrieval of OS files out-of-band.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15685
- https://docs.craftercms.org/en/3.0/security/advisory.html
- http://crafter.com
