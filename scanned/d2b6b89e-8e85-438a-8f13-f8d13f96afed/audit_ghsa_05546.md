# [M] go-tuf improperly validates the configured threshold for delegations

## Summary
Severity: Medium
Advisory: GHSA-fphv-w9fq-2525
CVE: CVE-2026-23992
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-fphv-w9fq-2525
Type: github-advisory

## Affected
- Go: `github.com/theupdateframework/go-tuf/v2` — affected >=0 <2.3.1

## Details
# Security Disclosure: Improper validation of configured threshold for delegations

## Summary

A compromised or misconfigured TUF repository can have the configured value of signature thresholds set to 0, which effectively disables signature verification. 

## Impact

Unathorized modification to TUF metadata files is possible at rest, or during transit as no integrity checks are made.

## Patches

Upgrade to v2.3.1

## Workarounds

Always make sure that the TUF metadata roles are configured with a threshold of at least 1.

## Affected code:

The `metadata.VerifyDelegate` did not verify the configured threshold prior to comparison. This means that a misconfigured TUF repository could disable the signature verification by setting the threshold to 0, or a negative value (and so always make the signature threshold computation to pass).

## References
- https://github.com/theupdateframework/go-tuf/security/advisories/GHSA-fphv-w9fq-2525
- https://nvd.nist.gov/vuln/detail/CVE-2026-23992
- https://github.com/theupdateframework/go-tuf/commit/b38d91fdbc69dfe31fe9230d97dafe527ea854a0
- https://github.com/theupdateframework/go-tuf
- https://github.com/theupdateframework/go-tuf/releases/tag/v2.3.1
