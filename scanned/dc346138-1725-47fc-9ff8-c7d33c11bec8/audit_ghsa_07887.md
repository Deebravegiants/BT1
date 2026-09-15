# [M] Centrifugo v6.6.0 dependency vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-j9wf-6r2x-hqmx
CWE: CWE-1395
Ecosystem: Go
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-j9wf-6r2x-hqmx
Type: github-advisory

## Affected
- Go: `github.com/centrifugal/centrifugo/v6` — affected >=0 <6.6.1

## Details
### Summary                                                                                                                                                                                              
                                                                                                                                                                                                           
  Centrifugo v6.6.0 binary is compiled with **Go 1.25.5** and                                                                                                                       
  statically links `github.com/quic-go/webtransport-go v0.9.0`, having **7 known                                                                                                                      
  CVEs**

  **Go standard library — compiled with Go 1.25.5:**

  | CVE | Severity | CVSS | Fixed In |
  |-----|----------|------|----------|
  | CVE-2025-68121 | **CRITICAL** | 10.0 | Go 1.25.7, 1.24.13 |
  | CVE-2025-61726 | HIGH | 7.5 | Go 1.25.6, 1.24.12 |
  | CVE-2025-61728 | MEDIUM | 6.5 | Go 1.25.6, 1.24.12 |
  | CVE-2025-61730 | MEDIUM | 5.3 | Go 1.25.6, 1.24.12 |

  **Direct dependency `github.com/quic-go/webtransport-go` — pinned at v0.9.0
  (`go.mod` line 34):**

  | CVE | Severity | CVSS | Fixed In |
  |-----|----------|------|----------|
  | CVE-2026-21434 | MEDIUM | 5.3 | webtransport-go v0.10.0 |
  | CVE-2026-21435 | MEDIUM | 5.3 | webtransport-go v0.10.0 |
  | CVE-2026-21438 | MEDIUM | 5.3 | webtransport-go v0.10.0 |

## References
- https://github.com/centrifugal/centrifugo/security/advisories/GHSA-j9wf-6r2x-hqmx
- https://github.com/centrifugal/centrifugo
- https://github.com/centrifugal/centrifugo/releases/tag/v6.6.1
