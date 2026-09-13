# [H] melange pipeline working-directory could allow command injection

## Summary
Severity: High
Advisory: GHSA-vqqr-rmpc-hhg2
CVE: CVE-2026-24844
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-vqqr-rmpc-hhg2
Type: github-advisory

## Affected
- Go: `chainguard.dev/melange` — affected >=0.3.0 <0.40.3

## Details
An attacker who can provide build input values, but not modify pipeline definitions, could execute arbitrary shell commands if the pipeline uses `${{vars.*}}` or `${{inputs.*}}` substitutions in `working-directory`. The field is embedded into shell scripts without proper quote escaping.

**Fix:** Fixed with [e51ca30c](https://github.com/chainguard-dev/melange/commit/e51ca30cfb63178f5a86997d23d3fff0359fa6c8), Released. 

**Acknowledgements**

melange thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/melange/security/advisories/GHSA-vqqr-rmpc-hhg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-24844
- https://github.com/chainguard-dev/melange/commit/e51ca30cfb63178f5a86997d23d3fff0359fa6c8
- https://github.com/chainguard-dev/melange
