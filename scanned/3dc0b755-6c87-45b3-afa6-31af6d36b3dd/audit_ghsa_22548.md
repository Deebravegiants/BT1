# [M] Several Zend Products Vulnerable to XXE and XEE attacks

## Summary
Severity: Medium
Advisory: GHSA-5wm2-38q5-5rxv
CVE: CVE-2014-2683
CWE: CWE-611, CWE-776
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5wm2-38q5-5rxv
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=0 <1.12.4
- Packagist: `zendframework/zendopenid` — affected >=0 <2.0.2
- Packagist: `zendframework/zendrest` — affected >=0 <2.0.2
- Packagist: `zendframework/zendservice-audioscrobbler` — affected >=0 <2.0.2
- Packagist: `zendframework/zendservice-nirvanix` — affected >=0 <2.0.2
- Packagist: `zendframework/zendservice-slideshare` — affected >=0 <2.0.2
- Packagist: `zendframework/zendservice-technorati` — affected >=0 <2.0.2
- Packagist: `zendframework/zendservice-windowsazure` — affected >=0 <2.0.2
- Packagist: `zendframework/zendservice-amazon` — affected >=0 <2.0.3
- Packagist: `zendframework/zendservice-api` — affected >=0 <1.0.0

## Details
Zend Framework 1 (ZF1) before 1.12.4, Zend Framework 2 before 2.1.6 and 2.2.x before 2.2.6, ZendOpenId, ZendRest, ZendService_AudioScrobbler, ZendService_Nirvanix, ZendService_SlideShare, ZendService_Technorati, and ZendService_WindowsAzure before 2.0.2, ZendService_Amazon before 2.0.3, and ZendService_Api before 1.0.0 allow remote attackers to cause a denial of service (CPU consumption) via (1) recursive or (2) circular references in an XML entity definition in an XML DOCTYPE declaration, aka an XML Entity Expansion (XEE) attack.  NOTE: this issue exists because of an incomplete fix for CVE-2012-6532.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2683
- https://web.archive.org/web/20140419041226/http://www.securityfocus.com/bid/66358
- https://web.archive.org/web/20150523055201/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2014:072/?name=MDVSA-2014:072
- http://advisories.mageia.org/MGASA-2014-0151.html
- http://framework.zend.com/security/advisory/ZF2014-01
- http://seclists.org/oss-sec/2014/q2/0
- http://www.debian.org/security/2015/dsa-3265
