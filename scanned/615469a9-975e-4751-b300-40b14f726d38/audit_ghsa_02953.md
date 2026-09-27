# [M] Misconfigured IP address field in ROA leads to OctoRPKI crash

## Summary
Severity: Medium
Advisory: GHSA-w6ww-fmfx-2x22
CVE: CVE-2021-3911
CWE: CWE-20, CWE-252
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-w6ww-fmfx-2x22
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.0

## Details
If the ROA that a repository returns contains too many bits for the IP address then OctoRPKI will crash.

## Patches

## For more information
If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-w6ww-fmfx-2x22
- https://nvd.nist.gov/vuln/detail/CVE-2021-3911
- https://github.com/cloudflare/cfrpki/commit/2882307febd66801de97b2a2ce4d93fe58132005
- https://github.com/cloudflare/cfrpki
- https://pkg.go.dev/vuln/GO-2022-0252
- https://www.debian.org/security/2022/dsa-5041
