# [M] apko affected by unbounded resource consumption in expandapk.Split on attacker-controlled .apk streams 

## Summary
Severity: Medium
Advisory: GHSA-6p9p-q6wh-9j89
CVE: CVE-2026-25122
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-6p9p-q6wh-9j89
Type: github-advisory

## Affected
- Go: `chainguard.dev/apko` — affected >=0.14.8 <1.1.0

## Details
`expandapk.Split` drains the first gzip stream of an APK archive via `io.Copy(io.Discard, gzi)` without explicit bounds. With an attacker-controlled input stream, this can force large gzip inflation work and lead to resource exhaustion (availability impact).                                                                                                                      
                                                                                                                                                                                              
The `Split` function reads the first tar header, then drains the remainder of the gzip stream by reading from the gzip reader directly without any maximum uncompressed byte limit or inflate-ratio cap. A caller that parses attacker-controlled APK streams may be forced to spend excessive CPU time inflating gzip data, leading to timeouts or process slowdown.             
                                                                                                                                                                                              
**Fix:** Fixed with [2be3903](https://github.com/chainguard-dev/apko/commit/2be3903fe194ad46351840f0569b35f5ac965f09), Released in v1.1.0.                                                  
                                                                                                                                                                                              
**Acknowledgements**                                                                                                                                                                        
                                                                                                                                                                                             
apko thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/apko/security/advisories/GHSA-6p9p-q6wh-9j89
- https://nvd.nist.gov/vuln/detail/CVE-2026-25122
- https://github.com/chainguard-dev/apko/commit/2be3903fe194ad46351840f0569b35f5ac965f09
- https://github.com/chainguard-dev/apko
