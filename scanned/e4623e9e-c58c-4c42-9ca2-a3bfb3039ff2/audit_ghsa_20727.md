# [H] cosign's `cosign verify-attestaton  --type` can report a false positive if any attestation exists

## Summary
Severity: High
Advisory: GHSA-vjxv-45g9-9296
CVE: CVE-2022-35929
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-10
Source: https://github.com/advisories/GHSA-vjxv-45g9-9296
Type: github-advisory

## Affected
- Go: `github.com/sigstore/cosign` — affected >=0 <1.10.1

## Details
`cosign verify-attestation` used with the `--type` flag will report a false positive verification when:

- There is at least one attestation with a valid signature
- There are NO attestations of the type being verified (--type defaults to "custom")

This can happen when signing with a standard keypair and with "keyless" signing with Fulcio. Users should upgrade to cosign version 1.10.1 or greater for a patch. Currently the only workaround is to upgrade.

## References
- https://github.com/sigstore/cosign/security/advisories/GHSA-vjxv-45g9-9296
- https://nvd.nist.gov/vuln/detail/CVE-2022-35929
- https://github.com/sigstore/cosign/commit/c5fda01a8ff33ca981f45a9f13e7fb6bd2080b94
- https://github.com/sigstore/cosign
