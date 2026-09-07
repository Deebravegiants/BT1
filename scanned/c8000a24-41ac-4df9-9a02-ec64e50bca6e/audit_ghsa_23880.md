# [C] XML External Entity Reference in Apache Sling

## Summary
Severity: Critical
Advisory: GHSA-7g54-vgp6-jj5w
CVE: CVE-2016-6798
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7g54-vgp6-jj5w
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.xss` — affected >=0 <1.0.12
- Maven: `org.apache.sling:org.apache.sling.xss.compat` — affected >=0 <1.1.0

## Details
In the XSS Protection API module before 1.0.12 in Apache Sling, the method XSS.getValidXML() uses an insecure SAX parser to validate the input string, which allows for XXE attacks in all scripts which use this method to validate user input, potentially allowing an attacker to read sensitive data on the filesystem, perform same-site-request-forgery (SSRF), port-scanning behind the firewall or DoS the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6798
- https://github.com/apache/sling-org-apache-sling-xss/commit/de32b144ad2be3367559f6184d560db42a220529
- https://github.com/jensdietrich/xshady-release/tree/main/CVE-2016-6798
- https://lists.apache.org/thread.html/b72c3a511592ec70729b3ec2d29302b6ce87bbeab62d4745617a6bd0@%3Cdev.sling.apache.org%3E
- http://www.securityfocus.com/bid/99873
