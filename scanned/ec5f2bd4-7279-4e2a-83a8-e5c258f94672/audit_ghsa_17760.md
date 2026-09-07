# [H] XXE vulnerability in XSLT parsing in `org.hl7.fhir.publisher`

## Summary
Severity: High
Advisory: GHSA-8c3x-hq82-gjcm
CVE: CVE-2024-52807
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-24
Source: https://github.com/advisories/GHSA-8c3x-hq82-gjcm
Type: github-advisory

## Affected
- Maven: `org.hl7.fhir.publisher:org.hl7.fhir.publisher.cli` — affected >=0 <1.7.4
- Maven: `org.hl7.fhir.publisher:org.hl7.fhir.publisher.core` — affected >=0 <1.7.4

## Details
### Impact
XSLT transforms performed by various components are vulnerable to XML external entity injections. A processed XML file with a malicious DTD tag ( ]> could produce XML containing data from the host system. This impacts use cases where org.hl7.fhir.publisher is being used to within a host where external clients can submit XML.

A previous release provided an incomplete solution revealed by new testing. 

### Patches
This issue has been patched as of version 1.7.4

### Workarounds
None

### References
[Previous Advisory for Incomplete solution](https://github.com/HL7/fhir-ig-publisher/security/advisories/GHSA-59rq-22fm-x8q5)
[MITRE CWE](https://cwe.mitre.org/data/definitions/611.html)
[OWASP XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#transformerfactory)

## References
- https://github.com/HL7/fhir-ig-publisher/security/advisories/GHSA-59rq-22fm-x8q5
- https://github.com/HL7/fhir-ig-publisher/security/advisories/GHSA-8c3x-hq82-gjcm
- https://nvd.nist.gov/vuln/detail/CVE-2024-52807
- https://github.com/HL7/fhir-ig-publisher/commit/3560de2f486d688a3ddcf4aa54d8bdacea380c3d
- https://github.com/HL7/fhir-ig-publisher
- https://github.com/HL7/fhir-ig-publisher/compare/1.7.3...1.7.4
