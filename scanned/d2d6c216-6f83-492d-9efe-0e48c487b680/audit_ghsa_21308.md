# [C] TCPDF vulnerable to attackers triggering deserialization of arbitrary data

## Summary
Severity: Critical
Advisory: GHSA-5hw4-m7f3-hhx8
CVE: CVE-2018-17057
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-5hw4-m7f3-hhx8
Type: github-advisory

## Affected
- Packagist: `tecnickcom/tcpdf` — affected >=0 <6.2.22
- Packagist: `fooman/tcpdf` — affected >=0 <6.2.22
- Packagist: `la-haute-societe/tcpdf` — affected >=0 <6.2.22
- Packagist: `spoonity/tcpdf` — affected >=0 <6.2.22

## Details
An issue was discovered in TCPDF before 6.2.22. Attackers can trigger deserialization of arbitrary data via the `phar://` wrapper.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17057
- https://github.com/LimeSurvey/LimeSurvey/commit/1cdd78d27697b3150bb44aaa7af1a81062a591a5
- https://github.com/tecnickcom/TCPDF/commit/1861e33fe05f653b67d070f7c106463e7a5c26ed
- https://contao.org/en/news/security-vulnerability-cve-2018-17057.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/fooman/tcpdf/CVE-2018-17057.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/la-haute-societe/tcpdf/CVE-2018-17057.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/spoonity/tcpdf/CVE-2018-17057.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/tecnickcom/tcpdf/CVE-2018-17057.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/wallabag/tcpdf/CVE-2018-17057.yaml
- https://github.com/tecnickcom/TCPDF
- https://www.exploit-db.com/exploits/46634
- http://packetstormsecurity.com/files/152200/TCPDF-6.2.19-Deserialization-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/152360/LimeSurvey-Deserialization-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2019/Mar/36
