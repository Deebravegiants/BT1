# [H] Arbitrary filepath traversal via URI injection 

## Summary
Severity: High
Advisory: GHSA-cqh2-vc2f-q4fh
CVE: CVE-2021-3907
CWE: CWE-20, CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-cqh2-vc2f-q4fh
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.4

## Details
OctoRPKI does not escape a URI with a filename containing "..", this allows a repository to create a file, (ex.  `rsync://example.org/repo/../../etc/cron.daily/evil.roa`), which would then be written to disk outside the base cache folder. This could allow for remote code execution on the host machine OctoRPKI is running on. 

## Patches

## For more information
If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-3jhm-87m6-x959
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-cqh2-vc2f-q4fh
- https://nvd.nist.gov/vuln/detail/CVE-2021-3907
- https://github.com/cloudflare/cfrpki/commit/a053a808feeb3115c76b6cc263ee55598ce6e8cd
- https://github.com/cloudflare/cfrpki/commit/eb9cc4db7b7b79e44f56dfaa959fccdfb2af8284
- https://github.com/cloudflare/cfrpki
- https://pkg.go.dev/vuln/GO-2022-0248
- https://www.debian.org/security/2021/dsa-5033
- https://www.debian.org/security/2022/dsa-5041
