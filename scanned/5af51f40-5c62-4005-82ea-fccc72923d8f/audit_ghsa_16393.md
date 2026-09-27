# [H] SMTP smuggling in Apache James

## Summary
Severity: High
Advisory: GHSA-p5q9-86w4-2xr5
CVE: CVE-2023-51747
CWE: CWE-20, CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-p5q9-86w4-2xr5
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0 <3.7.5
- Maven: `org.apache.james:james-server` — affected >=3.8.0 <3.8.1

## Details
Apache James prior to versions 3.8.1 and 3.7.5 is vulnerable to SMTP smuggling.

A lenient behaviour in line delimiter handling might create a difference of interpretation between the sender and the receiver which can be exploited by an attacker to forge an SMTP envelop, allowing for instance to bypass SPF checks.

The patch implies enforcement of CRLF as a line delimiter as part of the DATA transaction.

We recommend James users to upgrade to non vulnerable versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51747
- https://github.com/apache/james-project/commit/d1ef102540e504c067b6c1721a6f1e7eee9c6fc6
- https://github.com/apache/james-project/commit/d5cd8bb098aa78d8d62c9645f3c532689ef1cb03
- https://github.com/apache/james-project
- https://lists.apache.org/thread/rxkwbkh9vgbl9rzx1fkllyk3krhgydko
- https://postfix.org/smtp-smuggling.html
- https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide
- http://www.openwall.com/lists/oss-security/2024/02/27/4
