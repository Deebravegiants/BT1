# [M] CVE-2021-29642

## Summary
Severity: Medium
Advisory: CVE-2021-29642
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/CVE-2021-29642
Type: osv

## Details
GistPad before 0.2.7 allows a crafted workspace folder to change the URL for the Gist API, which leads to leakage of GitHub access tokens.

## References
- https://vuln.ryotak.me/advisories/7
- https://github.com/lostintangent/gistpad/commit/230b05e8dea8d7ac5aae998bbe0a591d7f081b70
