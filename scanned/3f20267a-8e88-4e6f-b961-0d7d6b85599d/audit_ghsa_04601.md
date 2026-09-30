# [M] Gitea: Open Redirect via redirect_to

## Summary
Severity: Medium
Advisory: GHSA-j5r2-4c8j-xc3m
CVE: CVE-2026-25779
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-j5r2-4c8j-xc3m
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.26.0

## Details
### Details

Despite the validation within `urlIsRelative` in `modules/httplib/url.go`, an open redirect is still possible due to usage of directory traversal sequences plus a back-slash in the "redirect_to" parameter.

### PoC

When a user uses this URL to login:

`https://gitea.com/user/login?redirect_to=/a/../\example.com`

They would be redirected to `example.com` upon a successful login to their gitea account.

### Impact

* Phishing: Attackers can use trusted domain links to redirect victims to credential-harvesting pages
* OAuth/SSO Token Theft: In authentication flows, authorization codes or tokens may leak via redirect
* Referer Leakage: Sensitive URL parameters may be exposed to attacker domains via the Referer header
* Cache Poisoning: In deployments with shared caches, malicious redirects may be cached and served to other users

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-j5r2-4c8j-xc3m
- https://github.com/go-gitea/gitea
