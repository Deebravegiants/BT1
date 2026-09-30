# [M] Piwik (now Matomo) Vulnerable to Arbitrary Code Execution

## Summary
Severity: Medium
Advisory: GHSA-2qr8-h6pq-m27v
CVE: CVE-2011-4941
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2qr8-h6pq-m27v
Type: github-advisory

## Affected
- Packagist: `piwik/piwik` — affected >=1.2 <1.5
- Packagist: `matomo/matomo` — affected >=1.2 <1.5

## Details
Unspecified vulnerability in Piwik 1.2 through 1.4 allows remote attackers with the view permission to execute arbitrary code via unknown attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4941
- https://github.com/matomo-org/matomo
- https://web.archive.org/web/20110626223028/http://piwik.org/blog/2011/06/piwik-1-5-security-advisory
- http://www.openwall.com/lists/oss-security/2012/03/18/1
- http://www.openwall.com/lists/oss-security/2012/03/19/8
