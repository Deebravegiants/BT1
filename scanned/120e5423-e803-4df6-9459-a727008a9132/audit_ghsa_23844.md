# [H] Pimcore Vulnerable to PHP Object Injection Attacks

## Summary
Severity: High
Advisory: GHSA-g7pj-3v97-3vxp
CVE: CVE-2014-2921
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g7pj-3v97-3vxp
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=1.4.9 <2.2.0

## Details
The `getObjectByToken` function in `Newsletter.php` in the `Pimcore_Tool_Newsletter` module in pimcore 1.4.9 through 2.0.0 does not properly handle an object obtained by unserializing Lucene search data, which allows remote attackers to conduct PHP object injection attacks and execute arbitrary code via vectors involving a `Zend_Pdf_ElementFactory_Proxy` object and a pathname with a trailing `\0` character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2921
- https://github.com/pimcore/pimcore/commit/3cb2683e669b5644f180d362cfa9614c09bef280
- https://github.com/pedrib/PoC/blob/caa03645e256a8b50f1101c983d39586ebc467ee/advisories/pimcore-2.1.0.txt
- https://github.com/pedrib/PoC/blob/master/pimcore-2.1.0.txt
- https://github.com/pimcore/pimcore
- http://openwall.com/lists/oss-security/2014/04/21/1
- http://www.pimcore.org/en/resources/blog/pimcore+2.2+released_b442
