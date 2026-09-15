# [M] PocketFlow - Path Traversal in pocketflow-coding-agent Cookbook Example File Tools

## Summary
Severity: Medium
Advisory: CVE-2026-55747
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-55747
Type: osv

## Details
The pocketflow-coding-agent cookbook example in The-Pocket/PocketFlow implements a helper as a thin os.path.join(workdir, p) wrapper with no canonicalization or containment check, used unguarded by the ReadFile, ListFiles, PatchRead, and PatchApply file-access tools. Severity reflects that this affects an illustrative cookbook example rather than a core library API; applications that copy this pattern into production are affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55747.json
- https://github.com/The-Pocket/PocketFlow
- https://nvd.nist.gov/vuln/detail/CVE-2026-55747
