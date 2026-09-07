# [H] HAPI FHIR XML External Entity (XXE) vulnerability

## Summary
Severity: High
Advisory: GHSA-4cf2-cxp3-rjr7
CVE: CVE-2024-51132
CWE: CWE-601, CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-05
Source: https://github.com/advisories/GHSA-4cf2-cxp3-rjr7
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.convertors` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2016may` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu3` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4b` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r5` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.utilities` — affected >=0 <6.4.0
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.validation` — affected >=0 <6.4.0

## Details
An XML External Entity (XXE) vulnerability in HAPI FHIR before v6.4.0 allows attackers to access sensitive information or execute arbitrary code via supplying a crafted request containing malicious XML entities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51132
- https://github.com/hapifhir/org.hl7.fhir.core/commit/7ede053a5fca50cc2802884c661a241d51703a67
- https://github.com/JAckLosingHeart/CVE-2024-51132-POC
- https://github.com/hapifhir/org.hl7.fhir.core
