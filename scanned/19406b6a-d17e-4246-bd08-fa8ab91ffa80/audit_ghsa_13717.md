# [M] Gitsign's Rekor public keys fetched from upstream API instead of local TUF client.

## Summary
Severity: Medium
Advisory: GHSA-xvrc-2wvh-49vc
CVE: CVE-2023-47122
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-xvrc-2wvh-49vc
Type: github-advisory

## Affected
- Go: `github.com/sigstore/gitsign` — affected >=0.6.0 <0.8.0

## Details
### Impact

In certain versions of gitsign, Rekor public keys were fetched via the Rekor API, instead of through the local TUF client. If the upstream Rekor server happened to be compromised, gitsign clients could potentially be tricked into trusting incorrect signatures.

There is no known compromise the default public good instance (`rekor.sigstore.dev`) - anyone using this instance is unlikely to be affected.

### Patches

This was fixed in v0.8.0 via https://github.com/sigstore/gitsign/pull/399

### Workarounds

n/a

### References
_Are there any links users can visit to find out more?_

https://docs.sigstore.dev/about/threat-model/#sigstore-threat-model

## References
- https://github.com/sigstore/gitsign/security/advisories/GHSA-xvrc-2wvh-49vc
- https://nvd.nist.gov/vuln/detail/CVE-2023-47122
- https://github.com/sigstore/gitsign/pull/399
- https://github.com/sigstore/gitsign/commit/cd66ccb03c86a3600955f0c15f6bfeb75f697236
- https://docs.sigstore.dev/about/threat-model/#sigstore-threat-model
- https://github.com/sigstore/gitsign
