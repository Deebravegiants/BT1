# [M] MediaElement Vulnerable to Reflected XSS 

## Summary
Severity: Medium
Advisory: GHSA-277w-qpxr-2549
CVE: CVE-2016-4567
CWE: CWE-79
Ecosystem: Packagist, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-277w-qpxr-2549
Type: github-advisory

## Affected
- npm: `mediaelement` — affected >=0 <2.11.1
- Packagist: `contao-components/mediaelement` — affected >=2.14.2 <2.21.1
- Packagist: `contao/core` — affected >=3.0.0 <3.5.15

## Details
Cross-site scripting (XSS) vulnerability in flash/FlashMediaElement.swf in MediaElement.js before 2.21.0, as used in WordPress before 4.5.2, allows remote attackers to inject arbitrary web script or HTML via an obfuscated form of the jsinitfunction parameter, as demonstrated by "jsinitfunctio%gn."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4567
- https://github.com/johndyer/mediaelement/commit/34834eef8ac830b9145df169ec22016a4350f06e
- https://github.com/mediaelement/mediaelement/commit/34834eef8ac830b9145df169ec22016a4350f06e
- https://codex.wordpress.org/Version_4.5.2
- https://contao.org/en/news/contao-3_5_15.html
- https://core.trac.wordpress.org/changeset/37371
- https://gist.github.com/cure53/df34ea68c26441f3ae98f821ba1feb9c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao-components/mediaelement/CVE-2016-4567.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core/CVE-2016-4567.yaml
- https://github.com/johndyer/mediaelement/blob/master/changelog.md
- https://github.com/mediaelement/mediaelement/blob/b992ccf5f0c04a207d98bbb0868420751a61ec90/changelog.md?plain=1#L1024
- https://github.com/mediaelement/mediaelement/blob/master/changelog.md
- https://web.archive.org/web/20170205142412/http://www.securitytracker.com/id/1035818
- https://wordpress.org/news/2016/05/wordpress-4-5-2
- https://wpvulndb.com/vulnerabilities/8488
- http://www.openwall.com/lists/oss-security/2016/05/07/2
- http://www.securitytracker.com/id/1035818
