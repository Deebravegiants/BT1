# [H] getID3 is vulnerable to XML External Entity (XXE)

## Summary
Severity: High
Advisory: GHSA-5v43-55m5-qr8f
CVE: CVE-2014-2053
CWE: CWE-611
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5v43-55m5-qr8f
Type: github-advisory

## Affected
- Packagist: `james-heinrich/getid3` — affected >=0 <1.9.9

## Details
getID3() before 1.9.9, as used in ownCloud Server before 5.0.15 and 6.0.x before 6.0.2, allows remote attackers to read arbitrary files, cause a denial of service, or possibly have other impact via an XML External Entity (XXE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2053
- https://github.com/JamesHeinrich/getID3/commit/afbdaa044a9a0a9dff2f800bd670e231b3ec99b2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/james-heinrich/getid3/CVE-2014-2053.yaml
- https://github.com/JamesHeinrich/getID3
- https://wordpress.org/news/2014/08/wordpress-3-9-2
- http://getid3.sourceforge.net/source/changelog.txt
- http://owncloud.org/about/security/advisories/oC-SA-2014-006
- http://secunia.com/advisories/58002
- http://www.debian.org/security/2014/dsa-3001
