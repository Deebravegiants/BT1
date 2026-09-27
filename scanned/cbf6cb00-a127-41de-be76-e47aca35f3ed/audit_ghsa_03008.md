# [H] Improper Preservation of Permissions in github.com/cloudflare/cfrpki/cmd/octorpki

## Summary
Severity: High
Advisory: GHSA-3pqh-p72c-fj85
CVE: CVE-2021-3978
CWE: CWE-269, CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-3pqh-p72c-fj85
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.2

## Details
### Impact

When copying files with rsync, octorpki uses the "-a" flag 0, which forces rsync to copy binaries with the suid bit set as root. Since the provided service definition defaults to root (https://github.com/cloudflare/cfrpki/blob/master/package/octorpki.service) this could allow for a vector, when combined with another vulnerability that causes octorpki to process a malicious TAL file, for a local privilege escalation.  

## For more information

If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-3pqh-p72c-fj85
- https://nvd.nist.gov/vuln/detail/CVE-2021-3978
- https://github.com/cloudflare/cfrpki
