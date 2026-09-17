# [M] Symfony Host Header Injection vulnerability in the HttpFoundation component

## Summary
Severity: Medium
Advisory: GHSA-22pv-7v9j-hqxp
CVE: CVE-2013-4752
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-22pv-7v9j-hqxp
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.24
- Packagist: `symfony/symfony` — affected >=2.1.0 <2.1.12
- Packagist: `symfony/symfony` — affected >=2.2.0 <2.2.5
- Packagist: `symfony/symfony` — affected >=2.3.0 <2.3.3
- Packagist: `symfony/http-foundation` — affected >=2.0.0 <2.0.24
- Packagist: `symfony/http-foundation` — affected >=2.1.0 <2.1.12
- Packagist: `symfony/http-foundation` — affected >=2.2.0 <2.2.5
- Packagist: `symfony/http-foundation` — affected >=2.3.0 <2.3.3

## Details
Symfony 2.0.X before 2.0.24, 2.1.X before 2.1.12, 2.2.X before 2.2.5, and 2.3.X before 2.3.3 have an issue in the HttpFoundation component. The Host header can be manipulated by an attacker when the framework is generating an absolute URL. A remote attacker could exploit this vulnerability to inject malicious content into the Web application page and conduct various attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4752
- https://web.archive.org/web/20130901060826/http://www.securityfocus.com/bid/61715
- https://symfony.com/blog/security-releases-symfony-2-0-24-2-1-12-2-2-5-and-2-3-3-released
- https://github.com/symfony/symfony
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2013-4752.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2013-4752.yaml
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86374
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86373
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86372
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86371
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86370
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86369
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86368
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86367
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86366
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86365
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-4752
- http://lists.fedoraproject.org/pipermail/package-announce/2013-August/114450.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-August/114461.html
- http://symfony.com/blog/security-releases-symfony-2-0-24-2-1-12-2-2-5-and-2-3-3-released
