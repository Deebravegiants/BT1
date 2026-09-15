# [H] notation-go's verification bypass can cause users to verify the wrong artifact

## Summary
Severity: High
Advisory: GHSA-xhg5-42rf-296r
CVE: CVE-2023-33959
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-xhg5-42rf-296r
Type: github-advisory

## Affected
- Go: `github.com/notaryproject/notation-go` — affected >=0 <1.0.0-rc.6

## Details
### Impact
An attacker who controls or compromises a registry can lead a user to verify the wrong artifact.

### Patches
The problem has been fixed in the release [v1.0.0-rc.6](https://github.com/notaryproject/notation-go/releases/tag/v1.0.0-rc.6). Users should upgrade their notation-go library to [v1.0.0-rc.6](https://github.com/notaryproject/notation-go/releases/tag/v1.0.0-rc.6) or above.

### Workarounds
User should use secure and trusted container registries.

### Credits
The `notation` project would like to thank Adam Korczynski (@AdamKorcz) for responsibly disclosing the issue found during an security audit (facilitated by OSTIF and sponsored by CNCF) and Shiwei Zhang (@shizhMSFT), Pritesh Bandi (@priteshbandi)  for root cause analysis.

## References
- https://github.com/notaryproject/notation-go/security/advisories/GHSA-xhg5-42rf-296r
- https://nvd.nist.gov/vuln/detail/CVE-2023-33959
- https://github.com/notaryproject/notation-go/commit/39c8ed050a65cca3f3f308534acb612096735a64
- https://github.com/notaryproject/notation-go/commit/eba60f5aed9c9e05dee55324423c95fe34700b4c
- https://github.com/notaryproject/notation-go
- https://github.com/notaryproject/notation-go/releases/tag/v1.0.0-rc.6
