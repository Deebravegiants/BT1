# [H] OpenMRS has Vulnerability in FHIR2 Module Privileges

## Summary
Severity: High
Advisory: CVE-2025-46823
Aliases: GHSA-g5vq-w8v2-4x9j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-46823
Type: osv

## Details
openmrs-module-fhir2 provides the FHIR REST API and related services for OpenMRS, an open medical records system. In versions of the FHIR2 module prior to 2.5.0, privileges were not always correctly checked, which means that unauthorized users may have been able to add or edit data they were not supposed to be able to. All implementers should update to FHIR2 2.5.0 or newer as soon as is feasible to receive a patch.

## References
- https://github.com/openmrs/openmrs-module-fhir2/releases/tag/2.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46823.json
- https://github.com/openmrs/openmrs-module-fhir2/security/advisories/GHSA-g5vq-w8v2-4x9j
- https://nvd.nist.gov/vuln/detail/CVE-2025-46823
