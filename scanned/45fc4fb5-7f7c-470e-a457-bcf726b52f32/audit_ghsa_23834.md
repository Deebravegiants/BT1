# [M] ZF-Commons ZfcUser Vulnerable to XSS in Login Redirect

## Summary
Severity: Medium
Advisory: GHSA-33rh-5hvf-5jjp
CVE: CVE-2015-1039
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-33rh-5hvf-5jjp
Type: github-advisory

## Affected
- Packagist: `zf-commons/zfc-user` — affected >=0 <1.2.2

## Details
Cross-site scripting (XSS) vulnerability in `user/login.phtml` in ZF-Commons ZfcUser before 1.2.2 allows remote attackers to inject arbitrary web script or HTML via the redirect parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1039
- https://github.com/ZF-Commons/ZfcUser/issues/550
- https://github.com/ZF-Commons/ZfcUser/commit/baf0e460
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zf-commons/zfc-user/CVE-2015-1039.yaml
- https://github.com/ZF-Commons/ZfcUser
- https://web.archive.org/web/20150202091028/http://www.securityfocus.com/bid/71931
- http://www.openwall.com/lists/oss-security/2015/01/11/4
