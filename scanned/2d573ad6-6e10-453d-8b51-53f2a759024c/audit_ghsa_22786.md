# [H] CakePHPallows remote attackers to read arbitrary files via XML data containing external entity references

## Summary
Severity: High
Advisory: GHSA-5964-pq8r-4q62
CVE: CVE-2012-4399
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5964-pq8r-4q62
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=2.1.0-alpha <2.1.5
- Packagist: `cakephp/cakephp` — affected >=2.2.0-beta <2.2.1

## Details
The Xml class in CakePHP 2.1.x before 2.1.5 and 2.2.x before 2.2.1 allows remote attackers to read arbitrary files via XML data containing external entity references, aka an XML external entity (XXE) injection attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4399
- https://github.com/cakephp/cakephp
- http://bakery.cakephp.org/articles/markstory/2012/07/14/security_release_-_cakephp_2_1_5_2_2_1
- http://seclists.org/bugtraq/2012/Jul/101
- http://secunia.com/advisories/49900
- http://www.exploit-db.com/exploits/19863
- http://www.openwall.com/lists/oss-security/2012/09/03/1
- http://www.openwall.com/lists/oss-security/2012/09/03/2
- http://www.osvdb.org/84042
