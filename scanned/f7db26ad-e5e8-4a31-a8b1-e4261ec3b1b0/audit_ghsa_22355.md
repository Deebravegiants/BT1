# [M] Apache James Hupa Webmail application Cross-site Scripting Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-7crp-p2vc-69r7
CVE: CVE-2012-3536
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7crp-p2vc-69r7
Type: github-advisory

## Affected
- Maven: `org.apache.james.hupa:hupa-parent` — affected >=0 <0.0.3

## Details
Two XSS vulnerabilities were fixed in message list and view in the Hupa Webmail application from the Apache James project. An attacker could send a carefully crafted email to a user of Hupa which would trigger a XSS when the email was opened or when a list of messages were viewed. This issue was addressed in Hupa 0.0.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3536
- https://github.com/apache/james-hupa/commit/aff28a8117a49969b0fc8cc9926c19fa90146d8d
- https://james.apache.org/hupa/index.html
- http://svn.apache.org/viewvc?view=revision&revision=1373762
