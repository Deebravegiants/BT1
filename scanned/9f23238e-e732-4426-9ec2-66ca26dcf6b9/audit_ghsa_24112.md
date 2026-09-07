# [H] Apache Archiva vulnerable to Cross Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-hf4p-mhc8-x2gp
CVE: CVE-2017-5657
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hf4p-mhc8-x2gp
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva` — affected >=0 <2.2.3

## Details
Several REST service endpoints of Apache Archiva are not protected against Cross Site Request Forgery (CSRF) attacks. A malicious site opened in the same browser as the archiva site, may send an HTML response that performs arbitrary actions on archiva services, with the same rights as the active archiva session (e.g. administrator rights).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5657
- https://github.com/apache/archiva
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8@%3Ccommits.pulsar.apache.org%3E
- https://web.archive.org/web/20211206215453/https://securitytracker.com/id/1038528
- http://archiva.apache.org/security.html#CVE-2017-5657
- http://www.securityfocus.com/bid/98570
