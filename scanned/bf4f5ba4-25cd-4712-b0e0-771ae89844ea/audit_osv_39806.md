# [M] Pathling: Typed CRUD/search/batch providers can lead to server-wide PHI exfiltration and cross-resource mutation

## Summary
Severity: Medium
Advisory: CVE-2026-47663
Aliases: GHSA-q62q-2m46-r7rv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-47663
Type: osv

## Details
Pathling is a set of tools that make it easier to use FHIR and clinical terminology within health data analytics. Prior to version 2.0.0 of Pathling Server, Pathling's typed CRUD/search/batch FHIR surface allows an authenticated caller with only coarse operation authorities to act on attacker-chosen resource families because those entrypoints do not consistently enforce the documented per-resource `read` and `write` authorities. The documented authorization model requires an operation authority (e.g. `pathling:search`) to be paired with the matching per-resource `read` or `write` authority (e.g. `pathling:read:Patient`). Delete and batch are documented to require write authority for all referenced resource types. However, typed search, update, and related handlers are annotated only with `@OperationAccess(...)` and act on the provider-selected resource type without checking the corresponding per-resource authority. This is fixed in Pathling Server 2.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47663.json
- https://github.com/aehrc/pathling/security/advisories/GHSA-q62q-2m46-r7rv
- https://nvd.nist.gov/vuln/detail/CVE-2026-47663
