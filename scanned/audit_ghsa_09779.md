# [M] notes-mcp has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-vc5j-42hh-j3mr
CVE: CVE-2026-7212
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-vc5j-42hh-j3mr
Type: github-advisory

## Affected
- PyPI: `notes-mcp` — affected >=0

## Details
A security vulnerability has been detected in edvardlindelof notes-mcp up to 0.1.4. This affects an unknown function of the file notes_mcp.py. The manipulation of the argument root_dir/path leads to path traversal. The attack is possible to be carried out remotely. The exploit has been disclosed publicly and may be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7212
- https://github.com/edvardlindelof/notes-mcp/issues/2
- https://github.com/edvardlindelof/notes-mcp
- https://vuldb.com/submit/802084
- https://vuldb.com/vuln/359808
- https://vuldb.com/vuln/359808/cti
