# [H] Filestash skips TLS certificate verification process when sending out email verification codes

## Summary
Severity: High
Advisory: GHSA-mpvx-whpp-99xj
CVE: CVE-2024-41256
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-mpvx-whpp-99xj
Type: github-advisory

## Affected
- Go: `github.com/mickael-kerjean/filestash` — affected >=0

## Details
Default configurations in the ShareProofVerifier function of filestash v0.4 causes the application to skip the TLS certificate verification process when sending out email verification codes, possibly allowing attackers to access sensitive data via a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41256
- https://github.com/mickael-kerjean/filestash/issues/709
- https://gist.github.com/nyxfqq/a6da3fe6128b978ea1aaa5df639d5f98
- https://github.com/mickael-kerjean/filestash
- https://github.com/mickael-kerjean/filestash/blob/master/server/model/share.go#L132
- https://pkg.go.dev/vuln/GO-2024-3035
