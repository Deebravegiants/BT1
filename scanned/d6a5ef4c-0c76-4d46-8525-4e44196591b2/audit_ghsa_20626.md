# [H] PolicyController before 0.2.1 may bypass attestation verification

## Summary
Severity: High
Advisory: GHSA-739f-hw6h-7wq8
CVE: CVE-2022-35930
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-10
Source: https://github.com/advisories/GHSA-739f-hw6h-7wq8
Type: github-advisory

## Affected
- Go: `github.com/sigstore/policy-controller` — affected >=0 <0.2.1

## Details
PolicyController will report a false positive, resulting in an admission when it should not be admitted when:
 * There is at least one attestation with a valid signature
 * There are NO attestations of the type being verified (--type defaults to "custom")

Users should upgrade to cosign version 0.2.1 or greater for a patch. There are no known workarounds at this time.

## References
- https://github.com/sigstore/policy-controller/security/advisories/GHSA-739f-hw6h-7wq8
- https://nvd.nist.gov/vuln/detail/CVE-2022-35930
- https://github.com/sigstore/policy-controller/commit/e852af36fb7d42678b21d7e97503c25bd1fd05c8
- https://github.com/sigstore/policy-controller
- https://github.com/sigstore/policy-controller/releases/tag/v0.2.1
