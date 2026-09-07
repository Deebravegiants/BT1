# [M] melange has a path traversal in license-path which allows reading files outside workspace 

## Summary
Severity: Medium
Advisory: GHSA-2w4f-9fgg-q2v9
CVE: CVE-2026-25145
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-2w4f-9fgg-q2v9
Type: github-advisory

## Affected
- Go: `chainguard.dev/melange` — affected >=0.14.0 <0.40.3

## Details
An attacker who can influence a melange configuration file (e.g., through pull request-driven CI or build-as-a-service scenarios) could read arbitrary files from the host system. The `LicensingInfos` function in `pkg/config/config.go` reads license files specified in `copyright[].license-path` without validating that paths remain within the workspace directory, allowing path traversal via `../` sequences. The contents of the traversed file are embedded into the generated SBOM as license text, enabling exfiltration of sensitive data through build artifacts.                                                                                                                                                                      
                                                                                                                                                                                        
  Fix: Merged in commit 2f95c9f4
                                                                                                                                                                                        
  Acknowledgements                                                                                                                                                                      
                                                                                                                                                                                        
melange thanks Oleh Konko (@1seal) from 1seal for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/melange/security/advisories/GHSA-2w4f-9fgg-q2v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25145
- https://github.com/chainguard-dev/melange/commit/2f95c9f4355ed993f2670bf1bb82d88b0f65e9e4
- https://github.com/chainguard-dev/melange
