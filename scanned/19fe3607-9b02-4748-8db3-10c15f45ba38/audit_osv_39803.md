# [M] Pathling: Explicit oauthMetadataUrl in bulk-submit allows OAuth client credential exfiltration

## Summary
Severity: Medium
Advisory: CVE-2026-47660
Aliases: GHSA-245h-c573-9vr5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-47660
Type: osv

## Details
Pathling is a set of tools that make it easier to use FHIR and clinical terminology within health data analytics. Prior to version 2.0.0 of Pathling Server, Pathling's bulk-submit operation allows an allowed submitter to supply an explicit `oauthMetadataUrl` parameter that is not validated against `pathling.bulkSubmit.allowableSources`. When present, the bulk-submit OAuth flow trusts metadata and the returned `token_endpoint` from the caller-chosen location, then builds outbound OAuth client authentication directly from the submitter's stored credentials. This is fixed in Pathling Server 2.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47660.json
- https://github.com/aehrc/pathling/security/advisories/GHSA-245h-c573-9vr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-47660
