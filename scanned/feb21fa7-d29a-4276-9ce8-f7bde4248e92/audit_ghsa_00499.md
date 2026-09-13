# [H] Command injection in org.apache.tika:tika-core

## Summary
Severity: High
Advisory: GHSA-9r24-gp44-h3pm
CVE: CVE-2018-1335
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-9r24-gp44-h3pm
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-core` — affected >=1.7 <1.18

## Details
From Apache Tika versions 1.7 to 1.17, clients could send carefully crafted headers to tika-server that could be used to inject commands into the command line of the server running tika-server. This vulnerability only affects those running tika-server on a server that is open to untrusted clients. The mitigation is to upgrade to Tika 1.18.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1335
- https://access.redhat.com/errata/RHSA-2019:3140
- https://github.com/advisories/GHSA-9r24-gp44-h3pm
- https://lists.apache.org/thread.html/b3ed4432380af767effd4c6f27665cc7b2686acccbefeb9f55851dca@%3Cdev.tika.apache.org%3E
- https://www.exploit-db.com/exploits/46540
- http://packetstormsecurity.com/files/153864/Apache-Tika-1.17-Header-Command-Injection.html
- http://www.securityfocus.com/bid/104001
