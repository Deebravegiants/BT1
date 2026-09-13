# [M] Apache Syncope uses a weak PNRG

## Summary
Severity: Medium
Advisory: GHSA-4c72-mrhf-23cg
CVE: CVE-2014-3503
CWE: CWE-338
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4c72-mrhf-23cg
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope` — affected >=1.1.0 <1.1.8

## Details
Apache Syncope 1.1.x before 1.1.8 uses weak random values to generate passwords, which makes it easier for remote attackers to guess the password via a brute force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3503
- https://github.com/apache/syncope/commit/8e0045925a387ee211832c7e0709dd418cda1ad3
- https://syncope.apache.org/security.html#cve-2014-3503-insecure-random-implementations-used-to-generate-p
- https://web.archive.org/web/20140728093808/http://www.securityfocus.com/bid/68431
- https://web.archive.org/web/20201207014021/http://www.securityfocus.com/archive/1/532669/100/0/threaded
- http://packetstormsecurity.com/files/127375/Apache-Syncope-Insecure-Password-Generation.html
- http://svn.apache.org/viewvc?view=revision&revision=r1596537
