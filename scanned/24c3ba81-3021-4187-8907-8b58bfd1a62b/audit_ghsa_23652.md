# [H] EGroupware Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-5gx6-f2qq-475f
CVE: CVE-2010-3313
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5gx6-f2qq-475f
Type: github-advisory

## Affected
- Packagist: `egroupware/egroupware` — affected >=0 <1.6.003
- Packagist: `egroupware/egroupware` — affected >=9.1 <9.1.20100309
- Packagist: `egroupware/egroupware` — affected >=9.2 <9.2.20100309

## Details
`phpgwapi/js/fckeditor/editor/dialog/fck_spellerpages/spellerpages/serverscripts/spellchecker.php` in EGroupware 1.4.001+.002; 1.6.001+.002 and possibly other versions before 1.6.003; and EPL 9.1 before 9.1.20100309 and 9.2 before 9.2.20100309; allows remote attackers to execute arbitrary commands via shell metacharacters in the (1) aspell_path or (2) spellchecker_lang parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3313
- https://github.com/EGroupware/egroupware
- http://www.debian.org/security/2010/dsa-2013
- http://www.egroupware.org/news?item=93
- http://www.exploit-db.com/exploits/11777
- http://www.openwall.com/lists/oss-security/2010/09/21/7
