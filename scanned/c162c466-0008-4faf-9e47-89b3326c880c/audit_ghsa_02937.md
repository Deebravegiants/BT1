# [M] Infinite open connection causes OctoRPKI to hang forever

## Summary
Severity: Medium
Advisory: GHSA-8cvr-4rrf-f244
CVE: CVE-2021-3909
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-8cvr-4rrf-f244
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.0

## Details
OctoRPKI (github.com/cloudflare/cfrpki/cmd/octorpki) does not limit the length of a connection, allowing for a slowloris DOS attack to take place which makes OctoRPKI wait forever. Specifically, the repository that OctoRPKI sends HTTP requests to will keep the connection open for a day before a response is returned, but does keep drip feeding new bytes to keep the connection alive.

## Patches

## For more information
If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-8cvr-4rrf-f244
- https://nvd.nist.gov/vuln/detail/CVE-2021-3909
- https://github.com/cloudflare/cfrpki
- https://github.com/cloudflare/cfrpki/releases/tag/v1.4.0
- https://www.debian.org/security/2021/dsa-5033
- https://www.debian.org/security/2022/dsa-5041
