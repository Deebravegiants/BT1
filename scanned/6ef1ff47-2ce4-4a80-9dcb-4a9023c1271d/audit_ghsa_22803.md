# [M] Cross-Site Request Forgery in Apache Struts

## Summary
Severity: Medium
Advisory: GHSA-h4v9-jf2r-9h6m
CVE: CVE-2014-7809
CWE: CWE-352
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h4v9-jf2r-9h6m
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.20

## Details
Apache Struts 2.0.0 through 2.3.x before 2.3.20 uses predictable <s:token/> values, which allows remote attackers to bypass the CSRF protection mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7809
- https://github.com/apache/struts/commit/1f301038a751bf16e525607c3db513db835b2999
- https://github.com/apache/struts
- https://web.archive.org/web/20150201180327/http://www.securitytracker.com/id/1031309
- https://web.archive.org/web/20150820131625/http://www.securityfocus.com/bid/71548
- https://web.archive.org/web/20201023114849/http://www.securityfocus.com/archive/1/534175/100/0/threaded
- http://packetstormsecurity.com/files/129421/Apache-Struts-2.3.20-Security-Fixes.html
- http://struts.apache.org/docs/s2-023.html
