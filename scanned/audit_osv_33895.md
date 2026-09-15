# [C] pgai secrets exfiltration via `pull_request_target`

## Summary
Severity: Critical
Advisory: CVE-2025-52467
Aliases: GHSA-89qq-hgvp-x37m
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-52467
Type: osv

## Details
pgai is a Python library that transforms PostgreSQL into a retrieval engine for RAG and Agentic applications. Prior to commit 8eb3567, the pgai repository was vulnerable to an attack allowing the exfiltration of all secrets used in one workflow. In particular, the GITHUB_TOKEN with write permissions for the repository, allowing an attacker to tamper with all aspects of the repository, including pushing arbitrary code and releases. This issue has been patched in commit 8eb3567.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52467.json
- https://github.com/timescale/pgai/security/advisories/GHSA-89qq-hgvp-x37m
- https://nvd.nist.gov/vuln/detail/CVE-2025-52467
- https://github.com/timescale/pgai/commit/8eb356729c33560ce54b88b9a956960ad1e3ede8
- https://github.com/timescale/pgai/pull/742
