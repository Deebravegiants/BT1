# [M] Gogs has an Open Redirect via redirect_to

## Summary
Severity: Medium
Advisory: GHSA-xxhq-69mf-w8cr
CVE: CVE-2026-52802
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-xxhq-69mf-w8cr
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary
An open redirect vulnerability exists in Gogs where attacker-controlled `redirect_to` parameters can bypass validation, allowing redirection to arbitrary external sites.


### Details
All redirects in Gogs that are validated via the `IsSameSite` function are vulnerable:
```go
func IsSameSite(url string) bool {
    return len(url) >= 2 && url[0] == '/' && url[1] != '/' && url[1] != '\\'
}
```

The function only inspects the first two characters of the URL string. This check fails to account for directory traversal sequences followed by backslashes. For example:
```
/a/../\example.com
```

The `IsSameSite` function checks the input supplied to the `redirect_to` query parameter value `/a/../\example.com` and considers it valid.

Because web browsers normalize backslashes `\` to forward slashes `/`, the normalized URL becomes `//example.com`.

The normalized URL becomes:
```
//example.com
```

Resulting in a cross-origin redirect.

This affects all endpoints using the `redirect_to` query parameter, including login and other post-action flows.


### PoC

1. An attacker can provide a user with a link to login to Gogs with a `redirect_to` query parameter that redirects a user to a site the attacker wants them to visit:
```
http://192.168.236.132:3000/user/login?redirect_to=/a/../\example.com
```

<img width="1339" height="536" alt="image" src="https://github.com/user-attachments/assets/3c2a13b8-f0b7-42c2-a223-6f0ebf083589" />  

<br>
<br>

2. After the user successfully logs in, they would be redirected to the site an attacker wants them to visit:

<img width="1066" height="463" alt="image" src="https://github.com/user-attachments/assets/1726a3d9-6705-43cc-bdd2-90aad105d021" />

<img width="1097" height="396" alt="image" src="https://github.com/user-attachments/assets/376052f5-0e00-4d14-a548-fa75a6269530" />


### Impact
* Phishing: Attackers can use trusted domain links to redirect victims to credential-harvesting pages
* OAuth/SSO Token Theft: In authentication flows, authorization codes or tokens may leak via redirect
* Referer Leakage: Sensitive URL parameters may be exposed to attacker domains via the Referer header
* Cache Poisoning: In deployments with shared caches, malicious redirects may be cached and served to other users

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-xxhq-69mf-w8cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-52802
- https://github.com/gogs/gogs/pull/8322
- https://github.com/gogs/gogs/commit/c5da9631dc75f692f313373ae229c4d47ba6517f
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
