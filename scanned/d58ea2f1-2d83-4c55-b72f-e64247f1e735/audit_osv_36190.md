# [M] OpenCTI's GraphQL Mutations Allow Deletion of Unrelated Entities

## Summary
Severity: Medium
Advisory: CVE-2026-21886
Aliases: GHSA-mhmx-j75v-2m6x, PYSEC-2026-117
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-21886
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to version 6.9.1, the GraphQL mutations "IndividualDeletionDeleteMutation" is intended to allow users to delete individual entity objects respectively. However, it was observed that this mutation can be misused to delete unrelated and sensitive objects such as analyses reports etc. This behavior stems from the lack of validation in the API to ensure that the targeted object is contextually related to the mutation being executed. Version 6.9.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21886.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-mhmx-j75v-2m6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-21886
