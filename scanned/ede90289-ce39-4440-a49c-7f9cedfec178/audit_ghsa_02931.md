# [M] OctoRPKI crashes when processing GZIP bomb returned via malicious repository

## Summary
Severity: Medium
Advisory: GHSA-g9wh-3vrx-r7hg
CVE: CVE-2021-3912
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-g9wh-3vrx-r7hg
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.0

## Details
OctoRPKI tries to load the entire contents of a repository in memory, and in the case of a GZIP bomb, unzip it in memory, making it possible to create a repository that makes OctoRPKI run out of memory (and thus crash). 

## Patches

## For more information
If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-g9wh-3vrx-r7hg
- https://nvd.nist.gov/vuln/detail/CVE-2021-3912
- https://github.com/cloudflare/cfrpki/commit/648658b1b176a747b52645989cfddc73a81eacad
- https://pkg.go.dev/vuln/GO-2022-0253
- https://www.debian.org/security/2022/dsa-5041
- github.com/cloudflare/cfrpki
