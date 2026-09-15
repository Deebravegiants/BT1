# [M] OpenEMR has FHIR Patient Compartment Bypass in CareTeam Resource

## Summary
Severity: Medium
Advisory: CVE-2026-24487
Aliases: GHSA-4frq-f657-hwrc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-24487
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, an authorization bypass vulnerability in the FHIR CareTeam resource endpoint allows patient-scoped FHIR tokens to access care team data for all patients instead of being restricted to only the authenticated patient's data. This could potentially lead to unauthorized disclosure of Protected Health Information (PHI), including patient-provider relationships and care team structures across the entire system. The issue occurs because the `FhirCareTeamService` does not implement the `IPatientCompartmentResourceService` interface and does not pass the patient binding parameter to the underlying service, bypassing the patient compartment filtering mechanism. Version 8.0.0 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24487.json
- https://github.com/openemr/openemr/security/advisories/GHSA-4frq-f657-hwrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24487
- https://github.com/openemr/openemr/commit/5ce10a3961b73862aaf31eb30044ffe1018465cc
