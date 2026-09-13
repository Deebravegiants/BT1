# [M] Notation vulnerable to denial of service from high number of artifact signatures

## Summary
Severity: Medium
Advisory: GHSA-9m3v-v4r5-ppx7
CVE: CVE-2023-33957
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-9m3v-v4r5-ppx7
Type: github-advisory

## Affected
- Go: `github.com/notaryproject/notation` — affected >=0 <1.0.0-rc.6

## Details
### Impact
An attacker who controls or compromises a registry can make the registry serve an infinite number of signatures for the artifact, causing a denial of service to the host machine running `notation verify`.

### Patches
The problem has been fixed in the release [v1.0.0-rc.6](https://github.com/notaryproject/notation/releases/tag/v1.0.0-rc.6). Users should upgrade their notation packages to [v1.0.0-rc.6](https://github.com/notaryproject/notation/releases/tag/v1.0.0-rc.6) or above.

### Workarounds
User should use secure and trusted container registries.

### Credits
The `notation` project would like to thank Adam Korczynski (@AdamKorcz) for responsibly disclosing the issue found during an security audit (facilitated by OSTIF and sponsored by CNCF) and Shiwei Zhang (@shizhMSFT) for root cause analysis.

## References
- https://github.com/notaryproject/notation/security/advisories/GHSA-9m3v-v4r5-ppx7
- https://nvd.nist.gov/vuln/detail/CVE-2023-33957
- https://github.com/notaryproject/notation/commit/ed22fde52f6d70ae0b53521bd28c9ccafa868c24
- https://github.com/notaryproject/notation
- https://github.com/notaryproject/notation/releases/tag/v1.0.0-rc.6
