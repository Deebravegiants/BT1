# [H] Cross-Site Request Forgery in Filebrowser

## Summary
Severity: High
Advisory: GHSA-72wf-hwcq-65h9
CVE: CVE-2021-46398
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-05
Source: https://github.com/advisories/GHSA-72wf-hwcq-65h9
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.18.0

## Details
A Cross-Site Request Forgery (CSRF) vulnerability exists in Filebrowser < 2.18.0 that allows attackers to create a backdoor user with admin privilege and get access to the filesystem via a malicious HTML webpage that is sent to the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46398
- https://github.com/filebrowser/filebrowser/issues/1621
- https://github.com/filebrowser/filebrowser/commit/74b7cd8e81840537a8206317344f118093153e8d
- https://febin0x4e4a.blogspot.com/2022/01/critical-csrf-in-filebrowser.html
- https://febin0x4e4a.wordpress.com/2022/01/19/critical-csrf-in-filebrowser
- https://febinj.medium.com/critical-csrf-to-rce-in-filebrowser-865a3c34b8e7
- https://github.com/filebrowser/filebrowser
- https://pkg.go.dev/vuln/GO-2022-0563
- https://systemweakness.com/critical-csrf-to-rce-in-filebrowser-865a3c34b8e7
- http://packetstormsecurity.com/files/165885/FileBrowser-2.17.2-Code-Execution-Cross-Site-Request-Forgery.html
