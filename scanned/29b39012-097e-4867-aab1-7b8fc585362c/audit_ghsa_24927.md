# [H] PEAR::Auth potential authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-76rh-xv36-9mrc
CVE: CVE-2006-0868
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-76rh-xv36-9mrc
Type: github-advisory

## Affected
- Packagist: `pear/auth` — affected >=0 <1.2.4
- Packagist: `pear/auth` — affected >=1.3.0r1 <1.3.0r4

## Details
Multiple unspecified injection vulnerabilities in unspecified Auth Container back ends for PEAR::Auth before 1.2.4, and 1.3.x before 1.3.0r4, allow remote attackers to "falsify authentication credentials," related to the "underlying storage containers."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-0868
- https://exchange.xforce.ibmcloud.com/vulnerabilities/24854
- https://github.com/pear/Auth
- https://web.archive.org/web/20060315074736/http://securitytracker.com/alerts/2006/Feb/1015666.html
- https://web.archive.org/web/20060408105851/http://www.securityfocus.com/bid/16758
- https://web.archive.org/web/20201207144810/http://www.securityfocus.com/archive/1/425796/100/0/threaded
- http://pear.php.net/package/Auth/download/1.2.4
- http://pear.php.net/package/Auth/download/1.3.0r4
- http://www.gentoo.org/security/en/glsa/glsa-200603-13.xml
