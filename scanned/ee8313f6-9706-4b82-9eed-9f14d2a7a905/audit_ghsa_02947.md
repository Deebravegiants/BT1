# [M] Infinite certificate chain depth results in OctoRPKI running forever

## Summary
Severity: Medium
Advisory: GHSA-g5gj-9ggf-9vmq
CVE: CVE-2021-3908
CWE: CWE-400, CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-g5gj-9ggf-9vmq
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.0

## Details
OctoRPKI (github.com/cloudflare/cfrpki/cmd/octorpki) does not limit the depth of a certificate chain, allowing for a CA to create children in an ad-hoc fashion, thereby making tree traversal never end.

### For more information
If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-g5gj-9ggf-9vmq
- https://nvd.nist.gov/vuln/detail/CVE-2021-3908
- https://github.com/cloudflare/cfrpki
- https://github.com/cloudflare/cfrpki/releases/tag/v1.4.0
- https://www.debian.org/security/2022/dsa-5041
