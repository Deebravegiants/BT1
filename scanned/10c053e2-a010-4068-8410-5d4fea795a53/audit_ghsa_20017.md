# [M] AWS S3 Crypto SDK sends an unencrypted hash of the plaintext alongside the ciphertext as a metadata field

## Summary
Severity: Medium
Advisory: GHSA-6jvc-q2x7-pchv
CVE: CVE-2022-2582
CWE: CWE-326
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-6jvc-q2x7-pchv
Type: github-advisory

## Affected
- Go: `github.com/aws/aws-sdk-go` — affected >=0 <1.34.0

## Details
The AWS S3 Crypto SDK sends an unencrypted hash of the plaintext alongside the ciphertext as a metadata field. This hash can be used to brute force the plaintext, if the hash is readable to the attacker. AWS now blocks this metadata field, but older SDK versions still send it.

## References
- https://github.com/google/security-research/security/advisories/GHSA-76wf-9vgp-pj7w
- https://nvd.nist.gov/vuln/detail/CVE-2022-2582
- https://github.com/aws/aws-sdk-go/commit/35fa6ddf45c061e0f08d3a3b5119f8f4da38f6d1
- https://github.com/aws/aws-sdk-go
- https://pkg.go.dev/vuln/GO-2022-0391
