# [M] Joomla! doesn't configure .htaccess to apply certain security checks that "block common exploits" to SEF URLs

## Summary
Severity: Medium
Advisory: GHSA-mxr8-pcpg-m23j
CVE: CVE-2008-3228
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-mxr8-pcpg-m23j
Type: github-advisory

## Affected
- Packagist: `joomla/joomla-platform` — affected >=0 <1.5.4

## Details
Joomla! before 1.5.4 does not configure .htaccess to apply certain security checks that "block common exploits" to SEF URLs, which has unknown impact and remote attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-3228
- https://exchange.xforce.ibmcloud.com/vulnerabilities/44206
- https://github.com/joomla/joomla-platform
- https://web.archive.org/web/20080730154423/http://www.joomla.org/content/view/5180/1
- http://www.joomla.org/content/view/5180/1/1/1/#htaccess
- http://www.openwall.com/lists/oss-security/2008/07/12/2
