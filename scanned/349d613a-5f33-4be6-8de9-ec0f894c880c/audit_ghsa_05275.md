# [H] PDM  wheel installation leads to Path Traversal via overridden write_to_fs

## Summary
Severity: High
Advisory: GHSA-78v8-vpjp-cjqh
CVE: CVE-2026-47764
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-78v8-vpjp-cjqh
Type: github-advisory

## Affected
- PyPI: `pdm` — affected >=0 <2.27.0

## Details
InstallDestination.write_to_fs() in src/pdm/installers/installers.py overrides the base class to add symlink/hardlink support but replaces the safe _path_with_destdir() (which validates via Path.resolve() + is_relative_to()) with a bare os.path.join() that performs no path validation. A malicious wheel with traversal entries can write arbitrary files. Same class as Poetry CVE-2026-34591. Fix ready at: https://github.com/pdm-project/pdm/pull/3787.

## References
- https://github.com/pdm-project/pdm/security/advisories/GHSA-78v8-vpjp-cjqh
- https://github.com/pdm-project/pdm/pull/3787
- https://github.com/pdm-project/pdm
- https://github.com/pdm-project/pdm/releases/tag/2.27.0
