# [H] tiagorlampert CHAOS vulnerable to command injections

## Summary
Severity: High
Advisory: GHSA-p3j6-f45h-hw5f
CVE: CVE-2024-30850
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-p3j6-f45h-hw5f
Type: github-advisory

## Affected
- Go: `github.com/tiagorlampert/CHAOS` — affected >=0 <0.0.0-20220716132853-b47438d36e3a

## Details
An issue in tiagorlampert CHAOS v5.0.1 allows a remote attacker to execute arbitrary code via the BuildClient function within client_service.go

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-30850
- https://nvd.nist.gov/vuln/detail/CVE-2024-33434
- https://github.com/tiagorlampert/CHAOS/pull/95
- https://github.com/tiagorlampert/CHAOS/commit/1b451cf62582295b7225caf5a7b506f0bad56f6b
- https://github.com/tiagorlampert/CHAOS/commit/24c9e109b5be34df7b2bce8368eae669c481ed5e
- https://blog.chebuya.com/posts/remote-code-execution-on-chaos-rat-via-spoofed-agents
- https://gist.github.com/slimwang/d1ec6645ba9012a551ea436679244496
- https://github.com/tiagorlampert/CHAOS
