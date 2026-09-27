# [H] notation-go has excessive memory allocation on verification

## Summary
Severity: High
Advisory: GHSA-87x9-7grx-m28v
CVE: CVE-2023-25656
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-22
Source: https://github.com/advisories/GHSA-87x9-7grx-m28v
Type: github-advisory

## Affected
- Go: `github.com/notaryproject/notation-go` — affected >=0 <1.0.0-rc.3

## Details
### Impact

`notation-go` users will find their application using excessive memory when verifying signatures and the application will be finally killed, and thus availability is impacted.

### Patches

The problem has been patched in the release [v1.0.0-rc.3](https://github.com/notaryproject/notation-go/releases/tag/v1.0.0-rc.3). Users should upgrade their `notation-go` packages to `v1.0.0-rc.3` or above.

### Workarounds

Users can review their own trust policy file and check if the identity string contains `=#`. Meanwhile, users should only put trusted certificates in their trust stores referenced by their own trust policy files, and make sure the `authenticity` validation is set to `enforce`

### Credits

The `notation-go` project would like to thank Adam Korczynski (@AdamKorcz) for responsibly disclosing this issue during a security fuzzing audit sponsored by CNCF and Shiwei Zhang (@shizhMSFT) for root cause analysis and detailed vulnerability report.

### References

- [Resource exhaustion attacks](https://en.wikipedia.org/wiki/Resource_exhaustion_attack)

## References
- https://github.com/notaryproject/notation-go/security/advisories/GHSA-87x9-7grx-m28v
- https://nvd.nist.gov/vuln/detail/CVE-2023-25656
- https://github.com/notaryproject/notation-go/pull/275
- https://github.com/notaryproject/notation-go
- https://github.com/notaryproject/notation-go/releases/tag/v1.0.0-rc.3
