# [M] Coder vulnerable to post-auth URL redirection to untrusted site ('Open Redirect')

## Summary
Severity: Medium
Advisory: GHSA-wcx9-ccpj-hx3c
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-28
Source: https://github.com/advisories/GHSA-wcx9-ccpj-hx3c
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.16.0 <2.16.1
- Go: `github.com/coder/coder/v2` — affected >=2.15.0 <2.15.3
- Go: `github.com/coder/coder/v2` — affected >=2.3.1 <2.14.4

## Details
### Summary
An issue on Coder's login page allows attackers to craft a Coder URL that when clicked by a logged in user could redirect them to a website the attacker controls, e.g. https://google.com.

### Details
On the login page, Coder checks for the presence of a `redirect` query parameter. On successful login, the user would be redirected to the location of the parameter. Improper sanitization allows attackers to specify a URL outside of the Coder application to redirect users to.

### Impact
Coder users could potentially be redirected to a untrusted website if tricked into clicking a URL crafted by the attacker. Coder authentication tokens are **not** leaked to the resulting website.

To check if your deployment is vulnerable, visit the following URL for your Coder deployment:
- `https://<coder url>/login?redirect=https%3A%2F%2Fcoder.com%2Fdocs`

### Patched Versions
This vulnerability is remedied in
- v2.16.1
- v2.15.3
- v2.14.4

All versions prior to 2.3.1 are not affected.

### Thanks
- https://github.com/jchristov

### References
https://github.com/coder/coder/security/advisories/GHSA-wcx9-ccpj-hx3c
https://github.com/coder/coder/commit/69c1d981e3131e50d52b01f6a360abadaad699e6

## References
- https://github.com/coder/coder/security/advisories/GHSA-wcx9-ccpj-hx3c
- https://github.com/coder/coder/commit/69c1d981e3131e50d52b01f6a360abadaad699e6
- https://github.com/coder/coder
