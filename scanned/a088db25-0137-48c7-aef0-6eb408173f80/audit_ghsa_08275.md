# [M] Concrete CMS is vulnerable to IDOR in surveys

## Summary
Severity: Medium
Advisory: GHSA-8c7c-h7px-267g
CVE: CVE-2026-8337
CWE: CWE-565
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-8c7c-h7px-267g
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to IDOR in surveys. To be vulnerable, a site would have to be configured in such a way that both public and private surveys are present on the site. An unauthenticated attacker can vote in the restricted survey by submitting the restricted optionID through the public survey’s endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8337
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
