# [M] Cosign's verify-blob-attestation reports false positive when payload parsing fails

## Summary
Severity: Medium
Advisory: GHSA-w6c6-c85g-mmv6
CVE: CVE-2026-39395
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-w6c6-c85g-mmv6
Type: github-advisory

## Affected
- Go: `github.com/sigstore/cosign` — affected >=3.0.0 <3.0.6
- Go: `github.com/sigstore/cosign` — affected >=0 <2.6.3

## Details
## Description

`cosign verify-blob-attestation` may erroneously report a "Verified OK" result for attestations with malformed payloads or mismatched predicate types. For old-format bundles and detached signatures, this was due to a logic flaw in the error handling of the predicate type validation. For new-format bundles, the predicate type validation was bypassed completely.

## Impact

When `cosign verify-blob-attestation` is used without `--check-claims` set to `true`, an attestation that has a valid signature but a malformed or unparsable payload would be incorrectly validated. Additionally, systems relying on `--type <predicate type>` to reject attestations with mismatched types would be lead to trust the unexpected attestation type.

## Patches

v3.0.6, v2.6.3

## Workarounds

Always set `--check-claims=true` for attestation verification.

## References
- https://github.com/sigstore/cosign/security/advisories/GHSA-w6c6-c85g-mmv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-39395
- https://github.com/sigstore/cosign
