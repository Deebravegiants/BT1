# [M] Pathling has path traversal in $import-pnp manifest that enables read-capable SSRF via /jobs/{jobId}/{filename}

## Summary
Severity: Medium
Advisory: CVE-2026-47659
Aliases: GHSA-5h9r-m7r5-8jxq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-47659
Type: osv

## Details
Pathling is a set of tools that make it easier to use FHIR and clinical terminology within health data analytics. Prior to version 2.0.0 of Pathling Server, Pathling's `/$result` endpoint allows a caller who can obtain any valid async export job ID to supply `file` parameter values containing path traversal sequences. The handler verifies only the supplied `job` and never normalises or confines the requested `file` path to that job's `jobs/<jobId>` directory before opening it as a filesystem resource. Because async export scratch space lives under the same warehouse database root as persisted resource tables, an attacker can use their own export job to read other files from the warehouse. This is fixed in Pathling Server 2.0.0. The `$result` handler now resolves and canonicalizes the requested file path and rejects any request that escapes the job's `jobs/<jobId>` directory. As an interim mitigation, disable the async export operations (`pathling.operations.exportEnabled`, `patientExportEnabled`, `groupExportEnabled`, `bulkSubmitEnabled`) or enable authentication and restrict export capability to trusted callers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47659.json
- https://github.com/aehrc/pathling/security/advisories/GHSA-5h9r-m7r5-8jxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47659
