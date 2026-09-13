# [C] HAPI FHIR HTTP authentication leak in redirects

## Summary
Severity: Critical
Advisory: GHSA-p7m9-v2cm-2h7m
CVE: CVE-2026-33180
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-p7m9-v2cm-2h7m
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.utilities` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.convertors` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu3` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu3.support` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2016may` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.model` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4b` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r5` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.validation` — affected >=0 <6.9.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.validation.cli` — affected >=0 <6.9.0

## Details
### Impact
When setting headers in HTTP requests, the internal HTTP client sends headers first to the host in the initial URL but also, if asked to follow redirects and a 30X HTTP response code is returned, to the host mentioned in URL in the Location: response header value.

Sending the same set of headers to subsequent hosts is a problem as this header often contains privacy sensitive information or data that could allow others to impersonate the  client's request.

### Patches
This issue has been patched in release 6.8.3 

### Workarounds
None.

## References
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-p7m9-v2cm-2h7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33180
- https://github.com/hapifhir/org.hl7.fhir.core
