# [M] GitPython 3.1.59 Local File Content Oracle via --no-index

## Summary
Severity: Medium
Advisory: CVE-2026-87818
Aliases: GHSA-whh4-5q6c-9v3x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87818
Type: osv

## Details
GitPython 3.1.59 fails to restrict the --no-index option in the high-level diff API, allowing attackers to read arbitrary filesystem paths as repository operands. Attackers can combine --no-index with -I/--ignore-matching-lines to create a content-dependent Boolean oracle, repeatedly querying local files to recover single-line secrets through distinguishable success or error responses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87818.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-whh4-5q6c-9v3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-87818
- https://www.vulncheck.com/advisories/gitpython-3.1.59-local-file-content-oracle-via-no-index
