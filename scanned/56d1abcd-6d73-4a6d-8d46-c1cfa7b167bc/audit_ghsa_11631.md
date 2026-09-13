# [H] Black's vulnerable version parsing leads to RCE in GitHub Action

## Summary
Severity: High
Advisory: GHSA-v53h-f6m7-xcgm
CVE: CVE-2026-31900
CWE: CWE-20
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-v53h-f6m7-xcgm
Type: github-advisory

## Affected
- GitHub Actions: `psf/black` — affected >=0 <26.3.0

## Details
### Impact

Black provides a [GitHub action](https://black.readthedocs.io/en/stable/integrations/github_actions.html) for formatting code. This action supports an option, `use_pyproject: true`, for reading the version of Black to use from the repository `pyproject.toml`. A malicious pull request could edit pyproject.toml to use a direct URL reference to a malicious repository. This could lead to arbitrary code execution in the context of the GitHub Action. Attackers could then gain access to secrets or permissions available in the context of the action.

### Patches

Version 26.3.0 fixes this vulnerability by tightening the validation of the `version` field. Users who use the GitHub Action as `psf/black@stable` will automatically pick up this update.

### Workarounds

Do not use the `use_pyproject: true` option in the psf/black GitHub Action.

## References
- https://github.com/psf/black/security/advisories/GHSA-v53h-f6m7-xcgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-31900
- https://github.com/psf/black/commit/0a2560b981364dde4c8cf8ce9d164c40669a8611
- https://github.com/psf/black
