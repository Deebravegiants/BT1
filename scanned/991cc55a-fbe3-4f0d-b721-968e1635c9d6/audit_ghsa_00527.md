# [C] Eclipse RDF4j vulnerable to XML External Entity

## Summary
Severity: Critical
Advisory: GHSA-6xq8-pvg4-3mf3
CVE: CVE-2018-1000644
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-6xq8-pvg4-3mf3
Type: github-advisory

## Affected
- Maven: `org.eclipse.rdf4j:rdf4j-runtime` — affected >=0 <2.4.0

## Details
Eclipse RDF4j version < 2.4.0 Milestone 2 contains a XML External Entity (XXE) vulnerability in RDF4j XML parser parsing RDF files that can result in the disclosure of confidential data, denial of service, server side request forgery, port scanning. This attack appear to be exploitable via Specially crafted RDF file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000644
- https://github.com/eclipse/rdf4j/issues/1056
- https://0dd.zone/2018/08/05/rdf4j-XXE
- https://github.com/advisories/GHSA-6xq8-pvg4-3mf3
- https://github.com/eclipse/rdf4j
