# [M] Notation's default `maxSignatureAttempts` in `notation verify` enables an endless data attack

## Summary
Severity: Medium
Advisory: GHSA-rvrx-rrwh-r9p6
CVE: CVE-2023-33958
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-rvrx-rrwh-r9p6
Type: github-advisory

## Affected
- Go: `github.com/notaryproject/notation` — affected >=0 <1.0.0-rc.6

## Details
### Impact
An attacker who controls or compromises a registry can make the registry serve an infinite number of signatures for the artifact, causing a denial of service to the host machine running `notation verify`.

### Patches
The problem has been fixed in the release [v1.0.0-rc.6](https://github.com/notaryproject/notation/releases/tag/v1.0.0-rc.6). Users should upgrade their notation packages to [v1.0.0-rc.6](https://github.com/notaryproject/notation/releases/tag/v1.0.0-rc.6) or above.

### Workarounds
User should use secure and trusted container registries

### Credits
The `notation` project would like to thank Adam Korczynski (@AdamKorcz) for responsibly disclosing the issue found during an security audit (facilitated by OSTIF and sponsored by CNCF) and Shiwei Zhang (@shizhMSFT) for root cause analysis.

## References
- https://github.com/notaryproject/notation/security/advisories/GHSA-rvrx-rrwh-r9p6
- https://nvd.nist.gov/vuln/detail/CVE-2023-33958
- https://github.com/notaryproject/notation
- https://github.com/notaryproject/notation/releases/tag/v1.0.0-rc.6
