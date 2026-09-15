# [M] gomatrixserverlib and Dendrite vulnerable to incorrect parsing of the event default power level in event auth

## Summary
Severity: Medium
Advisory: GHSA-grvv-h2f9-7v9c
CVE: CVE-2022-36009
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-grvv-h2f9-7v9c
Type: github-advisory

## Affected
- Go: `github.com/matrix-org/dendrite` — affected >=0 <0.9.3
- Go: `github.com/matrix-org/gomatrixserverlib` — affected >=0 <0.0.0-20220815091947-723fd495dde8

## Details
### Impact

The power level parsing within gomatrixserverlib was failing to parse the `"events_default"` key of the `m.room.power_levels` event, defaulting the event default power level to zero in all cases.

In rooms where the `"events_default"` power level had been changed, this could result in events either being incorrectly authorised or rejected by Dendrite servers.

### Patches

gomatrixserverlib contains a fix as of commit `723fd49` and Dendrite 0.9.3 has been updated accordingly.

### Workarounds

Matrix rooms where the `"events_default"` power level has not been changed from the default of zero are not vulnerable.

### For more information

If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/gomatrixserverlib/security/advisories/GHSA-grvv-h2f9-7v9c
- https://nvd.nist.gov/vuln/detail/CVE-2022-36009
- https://github.com/matrix-org/gomatrixserverlib/commit/723fd495dde835d078b9f2074b6b62c06dea4575
- https://github.com/matrix-org/gomatrixserverlib
- https://matrix.org/docs/guides/moderation/#power-levels
- https://pkg.go.dev/vuln/GO-2022-0952
