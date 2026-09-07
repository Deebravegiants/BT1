# [M] Joomla! allows attackers to access cached pages

## Summary
Severity: Medium
Advisory: GHSA-8xqm-3qm5-qhfv
CVE: CVE-2008-3226
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-8xqm-3qm5-qhfv
Type: github-advisory

## Affected
- Packagist: `joomla/joomla-platform` — affected >=0 <1.5.4

## Details
The file caching implementation in Joomla! before 1.5.4 allows attackers to access cached pages via unknown attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-3226
- https://exchange.xforce.ibmcloud.com/vulnerabilities/43650
- https://github.com/joomla/joomla-platform
- https://web.archive.org/web/20080730154423/http://www.joomla.org/content/view/5180/1
- https://web.archive.org/web/20200228023838/https://www.securityfocus.com/bid/30125
- http://www.openwall.com/lists/oss-security/2008/07/12/2
