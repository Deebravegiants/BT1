# [C] mellium.im/sasl authentication failure due to insufficient nonce randomness

## Summary
Severity: Critical
Advisory: GHSA-gvfj-fxx3-j323
CVE: CVE-2022-48195
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-31
Source: https://github.com/advisories/GHSA-gvfj-fxx3-j323
Type: github-advisory

## Affected
- Go: `mellium.im/sasl` — affected >=0 <0.3.1

## Details
An issue was discovered in Mellium mellium.im/sasl before 0.3.1. When performing SCRAM-based SASL authentication, if the remote end advertises support for channel binding, no random nonce is generated (instead, the nonce is empty). This causes authentication to fail in the best case, but (if paired with a remote end that does not validate the length of the nonce) could lead to insufficient randomness being used during authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-48195
- https://codeberg.org/mellium/sasl
- https://codeberg.org/mellium/sasl/commit/e6cbf681b247c4efa1477eaad2cc47a01707b732
- https://codeberg.org/mellium/sasl/releases/tag/v0.3.1
- https://mellium.im/cve/cve-2022-48195
- https://pkg.go.dev/vuln/GO-2023-1268
