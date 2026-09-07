# [M] Open redirect in Apache Struts

## Summary
Severity: Medium
Advisory: GHSA-rpj9-r897-wc6q
CVE: CVE-2013-2248
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rpj9-r897-wc6q
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.15.1

## Details
The Struts 2 DefaultActionMapper used to support a method for short-circuit navigation state changes by prefixing parameters with "redirect:" or "redirectAction:", followed by a desired redirect target expression. This mechanism was intended to help with attaching navigational information to buttons within forms. Attackers could use this to redirect to arbitrary web sites and conduct phishing attacks.

In Struts 2 before 2.3.15.1 the information following "redirect:" or "redirectAction:" can easily be manipulated to redirect to an arbitrary location.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2248
- https://github.com/apache/struts/commit/3cfe34fefedcf0fdcfcb061c0aea34a715b7de6
- https://github.com/apache/struts/commit/630e1ba065a8215c4e9ac03bfb09be9d655c2b6e
- https://github.com/apache/struts
- https://issues.apache.org/jira/browse/WW-4140
- http://struts.apache.org/release/2.3.x/docs/s2-017.html
