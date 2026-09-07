# [M] sqlite-mcp has an Injection issue

## Summary
Severity: Medium
Advisory: GHSA-4j28-22qp-rjcf
CVE: CVE-2026-7206
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-4j28-22qp-rjcf
Type: github-advisory

## Affected
- PyPI: `sqlite-mcp` — affected >=0

## Details
A security flaw has been discovered in dubydu sqlite-mcp up to 0.1.0. The affected element is the function extract_to_json of the file src/entry.py. Performing a manipulation of the argument output_filename results in sql injection. Remote exploitation of the attack is possible. The exploit has been released to the public and may be used for attacks. The patch is named a5580cb992f4f6c308c9ffe6442b2e76709db548. Applying a patch is the recommended action to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7206
- https://github.com/dubydu/sqlite-mcp/issues/1
- https://github.com/dubydu/sqlite-mcp/pull/2
- https://github.com/dubydu/sqlite-mcp/commit/a5580cb992f4f6c308c9ffe6442b2e76709db548
- https://github.com/dubydu/sqlite-mcp
- https://vuldb.com/submit/802081
- https://vuldb.com/vuln/359806
- https://vuldb.com/vuln/359806/cti
