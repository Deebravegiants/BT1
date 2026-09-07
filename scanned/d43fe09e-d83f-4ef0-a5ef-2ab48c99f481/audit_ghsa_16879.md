# [M] Apache Zeppelin CSRF vulnerability in the Credentials page

## Summary
Severity: Medium
Advisory: GHSA-prvg-rh5h-74jr
CVE: CVE-2021-28656
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-prvg-rh5h-74jr
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-web` — affected >=0

## Details
Cross-Site Request Forgery (CSRF) vulnerability in Credential page of Apache Zeppelin allows an attacker to submit malicious request.  This issue affects Apache Zeppelin Apache Zeppelin version 0.9.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28656
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/dttzkkv4qyn1rq2fdv1r94otb1osxztc
- http://www.openwall.com/lists/oss-security/2024/04/09/3
