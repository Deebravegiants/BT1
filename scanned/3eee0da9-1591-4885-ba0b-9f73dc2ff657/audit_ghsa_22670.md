# [M] Apache Shindig PHP Sensitive Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-6jvw-rpw4-gj4x
CVE: CVE-2013-4295
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6jvw-rpw4-gj4x
Type: github-advisory

## Affected
- Maven: `org.apache.shindig:shindig-php` — affected >=2.5.0-beta1 <2.5.0-update1

## Details
The gadget renderer in Apache Shindig 2.5.0 for PHP allows remote attackers to obtain sensitive information via an XML document containing an external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4295
- https://github.com/apache/shindig
- http://archives.neohapsis.com/archives/bugtraq/2013-10/0104.html
- http://shindig.apache.org/security.html
- http://www.securityfocus.com/bid/63260
