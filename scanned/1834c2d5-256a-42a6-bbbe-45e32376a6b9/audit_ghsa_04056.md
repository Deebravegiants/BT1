# [M] Cross-site Scripting in Apache UIMA

## Summary
Severity: Medium
Advisory: GHSA-vm59-329q-p468
CVE: CVE-2018-8035
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-vm59-329q-p468
Type: github-advisory

## Affected
- Maven: `org.apache.uima:uima-ducc-web` — affected >=0 <3.0.0

## Details
This vulnerability relates to the user's browser processing of DUCC webpage input data.The javascript comprising Apache UIMA DUCC (<= 2.2.2) which runs in the user's browser does not sufficiently filter user supplied inputs, which may result in unintended execution of user supplied javascript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8035
- https://lists.apache.org/thread.html/2f49681259b375d53431605f1c557ef8a3ed0af01a488d2e1b330053@%3Cdev.uima.apache.org%3E
- https://uima.apache.org/security_report
- http://www.securityfocus.com/bid/108195
