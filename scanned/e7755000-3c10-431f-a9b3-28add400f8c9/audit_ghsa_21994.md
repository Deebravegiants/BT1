# [M] Improper Input Validation in Xerces

## Summary
Severity: Medium
Advisory: GHSA-w4jq-qh47-hvjq
CVE: CVE-2020-14338
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-w4jq-qh47-hvjq
Type: github-advisory

## Affected
- Maven: `xerces:xercesImpl` — affected >=0 <2.12.0.sp3

## Details
A flaw was found in Wildfly's implementation of Xerces, specifically in the way the XMLSchemaValidator class in the JAXP component of Wildfly enforced the "use-grammar-pool-only" feature. This flaw allows a specially-crafted XML file to manipulate the validation process in certain cases. This issue is the same flaw as CVE-2020-14621, which affected OpenJDK, and uses a similar code. All xerces jboss versions before 2.12.0.SP3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14338
- https://bugzilla.redhat.com/show_bug.cgi?id=1860054
- https://lists.apache.org/thread.html/rf96c5afb26b596b4b97883aa90b6c0b0fc4c26aaeea7123c21912103@%3Cj-users.xerces.apache.org%3E
