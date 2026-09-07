# [M] Open Redirect URL in Harbor

## Summary
Severity: Medium
Advisory: GHSA-5757-v49g-f6r7
CVE: CVE-2024-22244
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-5757-v49g-f6r7
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=0 <2.8.5
- Go: `github.com/goharbor/harbor` — affected >=2.9.0 <2.9.3
- Go: `github.com/goharbor/harbor` — affected >=2.10.0 <2.10.1

## Details
### Description
Under OIDC authentication mode, there is a redirect_url parameter exposed in the URL which is used to redirect the current user to the defined location after the successful OIDC login, This redirect_url can be an ambiguous URL and can be used to embed a phishing URL.
For example: if a user clicks the URL with a malicious redirect_url:
```
https://<harbor_hostnmae>/c/oidc/login?redirect_url=https://<redirect_domain>
```
It might redirect the current user without their knowledge to a malicious site, posing a potential risk.
To avoid this issue, the redirect_url should be checked if it is a local path when reading it from the original request URL. 
```
//src/core/controllers/oidc.go
...
redirectURL := oc.Ctx.Request.URL.Query().Get("redirect_url")
if !utils.IsLocalPath(redirectURL) {
    log.Errorf("invalid redirect url: %v", redirectURL)
    oc.SendBadRequestError(fmt.Errorf("cannot redirect to other site"))
    return
}
if err := oc.SetSession(redirectURLKey, redirectURL); err != nil {
...
```
### Impact
When Harbor is configured with OIDC authentication and users log in via a link outside the Harbor server, it might be vulnerable to an open redirect attack. This attack only involves the OIDC Harbor user, if the current Harbor instance is not configured with OIDC auth, the redirect_url doesn't exist and the Harbor instance is not vulnerable to the open redirect attack.

The following versions of Harbor are involved:
<=Harbor 2.8.4, <=Harbor 2.9.2, <= Harbor 2.10.0

### Patches
Harbor 2.8.5, Harbor 2.9.3, Harbor 2.10.1

### Workarounds
When the Harbor is configured with OIDC authentication, warn the user not to log into the Harbor through external links.

### References
N/A

### Credit
Thanks Arnaud Cordier (arnaud@cordier.work)

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-5757-v49g-f6r7
- https://nvd.nist.gov/vuln/detail/CVE-2024-22244
- https://github.com/goharbor/harbor
- https://pkg.go.dev/vuln/GO-2024-2915
