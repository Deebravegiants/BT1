# [M] notation-go's timestamp signature generation lacks certificate revocation check

## Summary
Severity: Medium
Advisory: GHSA-45v3-38pc-874v
CVE: CVE-2024-56138
CWE: CWE-299
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-13
Source: https://github.com/advisories/GHSA-45v3-38pc-874v
Type: github-advisory

## Affected
- Go: `github.com/notaryproject/notation-go` — affected >=1.2.0-beta.1 <1.3.0-rc.2

## Details
This issue was identified during Quarkslab's audit of the timestamp feature.

### Summary
During the timestamp signature generation, the revocation status of the certificate(s) used to generate the timestamp signature was not verified.

### Details
During timestamp signature generation, notation-go did not check the revocation status of the certificate chain used by the TSA. This oversight creates a vulnerability that could be exploited through a Man-in-The-Middle attack. An attacker could potentially use a compromised, intermediate, or revoked leaf certificate to generate a malicious countersignature, which would then be accepted and stored by `notation`.

### Impact
This could lead to denial of service scenarios, particularly in CI/CD environments during signature verification processes because timestamp signature would fail due to the presence of a revoked certificate(s) potentially disrupting operations.

## References
- https://github.com/notaryproject/notation-go/security/advisories/GHSA-45v3-38pc-874v
- https://nvd.nist.gov/vuln/detail/CVE-2024-56138
- https://github.com/notaryproject/notation-go/commit/e7005a6d13e5ba472d4e166fbb085152f909e102
- https://github.com/notaryproject/notation-go/commit/e99be1954a15673020150c5f8800b8174cd7428d
- https://github.com/notaryproject/notation-go
- https://pkg.go.dev/vuln/GO-2025-3381
