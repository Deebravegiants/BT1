# [H] XXE vulnerability in XSLT transforms in `org.hl7.fhir.core`

## Summary
Severity: High
Advisory: GHSA-6cr6-ph3p-f5rf
CVE: CVE-2024-45294
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-06
Source: https://github.com/advisories/GHSA-6cr6-ph3p-f5rf
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2016may` — affected >=0 <6.3.23
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu3` — affected >=0 <6.3.23
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4` — affected >=0 <6.3.23
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4b` — affected >=0 <6.3.23
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r5` — affected >=0 <6.3.23
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.utilities` — affected >=0 <6.3.23

## Details
### Impact
XSLT transforms performed by various components are vulnerable to XML external entity injections. A processed XML file with a malicious DTD tag ( `<!DOCTYPE foo [<!ENTITY example SYSTEM "/etc/passwd"> ]>` could produce XML containing data from the host system. This impacts use cases where org.hl7.fhir.core is being used to within a host where external clients can submit XML.

### Patches
This issue has been patched in release 6.3.23

### Workarounds
None.

### References
[MITRE CWE](https://cwe.mitre.org/data/definitions/611.html)
[OWASP XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#transformerfactory)

## References
- https://github.com/HL7/fhir-ig-publisher/security/advisories/GHSA-59rq-22fm-x8q5
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-6cr6-ph3p-f5rf
- https://nvd.nist.gov/vuln/detail/CVE-2024-45294
- https://github.com/HL7/fhir-ig-publisher/releases/tag/1.6.22
- https://github.com/hapifhir/org.hl7.fhir.core
- https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/6.3.23
