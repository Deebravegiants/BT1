# [M] Navidrome uses MD5 hashing algorithm

## Summary
Severity: Medium
Advisory: GHSA-hrmx-8jjv-g758
CVE: CVE-2024-41259
CWE: CWE-200, CWE-305, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-hrmx-8jjv-g758
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0

## Details
Use of insecure hashing algorithm in the Gravatar's service in Navidrome v0.52.3 allows attackers to manipulate a user's account information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41259
- https://gist.github.com/nyxfqq/d192af10b53a363e2d9e430068333e04
- https://github.com/navidrome/navidrome
- https://pkg.go.dev/vuln/GO-2024-3029
