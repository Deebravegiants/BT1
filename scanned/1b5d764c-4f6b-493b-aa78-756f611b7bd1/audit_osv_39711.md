# [H] conda-smithy vulnerable to misrouted repository invitation by conda-forge-webservices[bot] due to GitHub username takeover leading to unintended write access in conda-forge feedstock repository

## Summary
Severity: High
Advisory: CVE-2026-46699
Aliases: GHSA-g95q-3cmj-fvh8
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-46699
Type: osv

## Details
conda-smithy is a tool for combining a conda recipe with configurations to build using freely hosted CI services into a single repository. Prior to version 3.61.0, a vulnerability in the conda-forge automated webservices allowed unintended write access to feedstock repositories through GitHub username takeover. The root cause is the use of mutable GitHub usernames as identifiers for repository invitation routing, rather than stable, immutable GitHub user IDs. Version 3.61.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46699.json
- https://github.com/conda-forge/conda-smithy/security/advisories/GHSA-g95q-3cmj-fvh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-46699
- https://github.com/conda-forge/conda-smithy/commit/3b0bcd92ebd6f41edd341401d84583a20911c587
