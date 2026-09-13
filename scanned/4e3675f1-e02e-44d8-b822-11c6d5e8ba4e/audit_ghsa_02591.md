# [H] XML External Entity Reference in Apache Jena

## Summary
Severity: High
Advisory: GHSA-7rp6-w7mg-h8rw
CVE: CVE-2021-39239
CWE: CWE-611
Ecosystem: Maven
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-7rp6-w7mg-h8rw
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena-core` — affected >=0 <4.2.0

## Details
A vulnerability in XML processing in Apache Jena, in versions up to 4.1.0, may allow an attacker to execute XML External Entities (XXE), including exposing the contents of local files to a remote server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39239
- https://gitbox.apache.org/repos/asf?p=jena.git
- https://lists.apache.org/thread.html/r0f03ae7e102c3e8587fdd36531fc167309335738156dfbd7d9c1bf45@%3Cdev.jena.apache.org%3E
- https://lists.apache.org/thread.html/rce5241b228a1f0e5880f6b2bfdb7ae9ee420e94cb692738a0bbfed9d@%3Cdev.jena.apache.org%3E
- https://lists.apache.org/thread.html/rf44d529c54ef1d0097e813f576a0823a727e1669a9f610d3221d493d%40%3Cusers.jena.apache.org%3E
- https://lists.apache.org/thread.html/rf44d529c54ef1d0097e813f576a0823a727e1669a9f610d3221d493d@%3Cannounce.apache.org%3E
