# [M] Cross-site Scripting in HAPI FHIR

## Summary
Severity: Medium
Advisory: GHSA-52mh-p2m2-w625
CVE: CVE-2019-12741
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-07
Source: https://github.com/advisories/GHSA-52mh-p2m2-w625
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:hapi-fhir-base` — affected >=0 <3.8.0

## Details
XSS exists in the HAPI FHIR testpage overlay module of the HAPI FHIR library before 3.8.0. The attack involves unsanitized HTTP parameters being output in a form page, allowing attackers to leak cookies and other sensitive information from ca/uhn/fhir/to/BaseController.java via a specially crafted URL. (This module is not generally used in production systems so the attack surface is expected to be low, but affected systems are recommended to upgrade immediately.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12741
- https://github.com/jamesagnew/hapi-fhir/issues/1335
- https://github.com/jamesagnew/hapi-fhir/commit/8f41159eb147eeb964cad68b28eff97acac6ea9a
- https://github.com/jamesagnew/hapi-fhir/releases/tag/v3.8.0
