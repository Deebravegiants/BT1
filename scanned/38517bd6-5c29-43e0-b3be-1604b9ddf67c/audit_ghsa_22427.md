# [H] Zeta Components Mail Arbitrary code execution via a crafted email address

## Summary
Severity: High
Advisory: GHSA-hgr8-g756-vmg9
CVE: CVE-2017-15806
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hgr8-g756-vmg9
Type: github-advisory

## Affected
- Packagist: `zetacomponents/mail` — affected >=0 <1.8.2

## Details
The send function in the ezcMailMtaTransport class in Zeta Components Mail before 1.8.2 does not properly restrict the set of characters used in the ezcMail returnPath property, which might allow remote attackers to execute arbitrary code via a crafted email address, as demonstrated by one containing "-X/path/to/wwwroot/file.php."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15806
- https://github.com/zetacomponents/Mail/issues/58
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zetacomponents/mail/CVE-2017-15806.yaml
- https://github.com/zetacomponents/Mail
- https://github.com/zetacomponents/Mail/releases/tag/1.8.2
- https://kay-malwarebenchmark.github.io/blog/cve-2017-15806-critical-rce-vulnerability
- https://kay-malwarebenchmark.github.io/blog/cve-2017-15806-yuan-cheng-dai-ma-zhi-xing-lou-dong
- https://www.exploit-db.com/exploits/43155
- http://www.securityfocus.com/bid/101866
