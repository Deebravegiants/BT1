# [C] qdrant input validation failure 

## Summary
Severity: Critical
Advisory: GHSA-7m75-x27w-r52r
CVE: CVE-2024-3829
CWE: CWE-20, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-7m75-x27w-r52r
Type: github-advisory

## Affected
- PyPI: `qdrant-client` — affected >=0 <1.9.0

## Details
qdrant/qdrant version 1.9.0-dev is vulnerable to arbitrary file read and write during the snapshot recovery process. Attackers can exploit this vulnerability by manipulating snapshot files to include symlinks, leading to arbitrary file read by adding a symlink that points to a desired file on the filesystem and arbitrary file write by including a symlink and a payload file in the snapshot's directory structure. This vulnerability allows for the reading and writing of arbitrary files on the server, which could potentially lead to a full takeover of the system. The issue is fixed in version v1.9.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3829
- https://github.com/qdrant/qdrant/commit/ee7a31ec3459a6a4219200234615c1817ab82260
- https://github.com/qdrant/qdrant-client
- https://huntr.com/bounties/abd9c906-75ee-4d84-b76d-ce1386401e08
