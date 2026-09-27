# [H] ImpressPages CMS eval injection vulnerability

## Summary
Severity: High
Advisory: GHSA-fr34-mx6j-vpxh
CVE: CVE-2011-4932
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fr34-mx6j-vpxh
Type: github-advisory

## Affected
- Packagist: `impresspages/impresspages` — affected >=0 <1.0.13

## Details
Eval injection vulnerability in `ip_cms/modules/standard/content_management/actions.php` in ImpressPages CMS 1.0.12 and possibly other versons before 1.0.13 allows remote attackers to execute arbitrary code via the `cm_group` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4932
- https://github.com/impresspages/ImpressPages
- https://web.archive.org/web/20120726055617/http://www.securityfocus.com/bid/49798
- https://web.archive.org/web/20120726081336/http://www.impresspages.org/news/impresspages-1-0-13-security-release
- http://seclists.org/bugtraq/2011/Sep/156
- http://www.openwall.com/lists/oss-security/2012/01/15/9
- http://www.openwall.com/lists/oss-security/2012/01/18/12
