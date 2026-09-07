# [H] Filestash configured to skip TLS certificate verification when using the FTPS protocol

## Summary
Severity: High
Advisory: GHSA-4jmm-c6jw-g796
CVE: CVE-2024-41255
CWE: CWE-295, CWE-453
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-4jmm-c6jw-g796
Type: github-advisory

## Affected
- Go: `github.com/mickael-kerjean/filestash` — affected >=0

## Details
filestash v0.4 is configured to skip TLS certificate verification when using the FTPS protocol, possibly allowing attackers to execute a man-in-the-middle attack via the Init function of index.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41255
- https://github.com/mickael-kerjean/filestash/issues/710
- https://gist.github.com/nyxfqq/c367f2ca9448810924dcf0f1af30b441
- https://github.com/advisories/GHSA-4jmm-c6jw-g796
- https://github.com/mickael-kerjean/filestash
- https://github.com/mickael-kerjean/filestash/blob/master/server/plugin/plg_backend_ftp/index.go#L108
- https://pkg.go.dev/vuln/GO-2024-3033
