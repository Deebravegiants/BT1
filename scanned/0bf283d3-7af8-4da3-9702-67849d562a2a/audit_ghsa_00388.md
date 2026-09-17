# [M] Apache Tika Server exposes sensitive information

## Summary
Severity: Medium
Advisory: GHSA-ccjp-w723-2jf2
CVE: CVE-2015-3271
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-ccjp-w723-2jf2
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-server` — affected >=0 <1.10

## Details
Apache Tika provides optional functionality to run itself as a web service to allow remote use. When used in this manner,
it's possible for a 3rd party to pass a 'fileUrl' header to the Apache Tika Server (tika-server) before version 1.10. This header lets a remote client request that the server fetches content from the URL provided, including files from the server's local filesystem. Depending on the file permissions set on the local filesystem, this could be used to return sensitive content from the server machine.

This vulnerability only exists if you are running the tika-server version 1.9, and you allow un-trusted access to the tika-server
URL. Usage of Apache Tika as a standard library is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3271
- https://github.com/advisories/GHSA-ccjp-w723-2jf2
- https://github.com/apache/tika
- https://lists.apache.org/thread.html/d2b3e7afb0251fac95fdee9817423cbc91e3d99a848c25a51d91c1e8%401439485507%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/d2b3e7afb0251fac95fdee9817423cbc91e3d99a848c25a51d91c1e8@1439485507@%3Cdev.tika.apache.org%3E
- http://www.openwall.com/lists/oss-security/2015/08/13/5
- http://www.securityfocus.com/bid/95020
