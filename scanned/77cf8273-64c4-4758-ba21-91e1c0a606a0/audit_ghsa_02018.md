# [M] Uncontrolled Resource Consumption in JPA Server in HAPI FHIR

## Summary
Severity: Medium
Advisory: GHSA-67f6-c8mx-4q2m
CVE: CVE-2021-32053
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-67f6-c8mx-4q2m
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:hapi-fhir-jpaserver-base` — affected >=0 <5.4.0

## Details
JPA Server in HAPI FHIR before 5.4.0 allows a user to deny service (e.g., disable access to the database after the attack stops) via history requests. This occurs because of a SELECT COUNT statement that requires a full index scan, with an accompanying large amount of server resources if there are many simultaneous history requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32053
- https://github.com/hapifhir/hapi-fhir/issues/2641
- https://github.com/hapifhir/hapi-fhir/pull/2642
- https://hapifhir.io
