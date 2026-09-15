# [H] apko has a path traversal in apko dirFS which allows filesystem writes outside base

## Summary
Severity: High
Advisory: GHSA-5g94-c2wx-8pxw
CVE: CVE-2026-25121
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-5g94-c2wx-8pxw
Type: github-advisory

## Affected
- Go: `chainguard.dev/apko` — affected >=0.14.8 <1.1.0

## Details
A Path Traversal vulnerability was discovered in apko's dirFS filesystem abstraction. An attacker who can supply a malicious APK package (e.g., via a compromised or typosquatted repository) could create directories or symlinks outside the intended installation root. The MkdirAll, Mkdir, and Symlink methods in pkg/apk/fs/rwosfs.go use filepath.Join() without validating that the resulting path stays within the base directory.

**Fix:** Fixed by [d8b7887](https://github.com/chainguard-dev/apko/commit/d8b7887a968a527791b3c591ae83928cb49a9f14). Merged into release. 

**Acknowledgements**                                                                                                                                                                        
                                                                                                                                                                                              
apko thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/apko/security/advisories/GHSA-5g94-c2wx-8pxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-25121
- https://github.com/chainguard-dev/apko/commit/d8b7887a968a527791b3c591ae83928cb49a9f14
- https://github.com/chainguard-dev/apko
