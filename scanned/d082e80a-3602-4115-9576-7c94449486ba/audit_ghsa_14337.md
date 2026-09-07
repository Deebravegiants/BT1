# [M] Lack of domain validation in Druple core

## Summary
Severity: Medium
Advisory: GHSA-4wfq-jc9h-vpcx
CVE: CVE-2022-25276
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-4wfq-jc9h-vpcx
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <9.3.19
- Packagist: `drupal/core` — affected >=9.4.0 <9.4.3

## Details
The Media oEmbed iframe route does not properly validate the iframe domain setting, which allows embeds to be displayed in the context of the primary domain. Under certain circumstances, this could lead to cross-site scripting, leaked cookies, or other vulnerabilities.

Drupal 7 core does not include the Media module and therefore is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25276
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2022-015
