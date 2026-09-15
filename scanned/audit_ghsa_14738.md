# [H] Ucum-java has an XXE vulnerability in XML parsing

## Summary
Severity: High
Advisory: GHSA-w9j7-phm3-f97j
CVE: CVE-2024-55887
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-13
Source: https://github.com/advisories/GHSA-w9j7-phm3-f97j
Type: github-advisory

## Affected
- Maven: `org.fhir:ucum` — affected >=0 <1.0.9

## Details
### Impact
XML parsing performed by the UcumEssenceService is vulnerable to XML external entity injections. A processed XML file with a malicious DTD tag could produce XML containing data from the host system. This impacts use cases where ucum is being used to within a host where external clients can submit XML.

### Patches
Release 1.0.9 of ucum fixes this vulnerability

### Workarounds
Ensure that the source xml for instantiating UcumEssenceService is trusted.

### References
* https://cwe.mitre.org/data/definitions/611.html
* https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#jaxp-documentbuilderfactory-saxparserfactory-and-dom4j

## References
- https://github.com/FHIR/Ucum-java/security/advisories/GHSA-w9j7-phm3-f97j
- https://nvd.nist.gov/vuln/detail/CVE-2024-55887
- https://github.com/FHIR/Ucum-java
