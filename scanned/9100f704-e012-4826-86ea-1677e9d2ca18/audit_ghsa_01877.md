# [M] The pattern '/\domain.com' is not disallowed when redirecting, allowing for open redirect

## Summary
Severity: Medium
Advisory: GHSA-qqxw-m5fj-f7gv
CVE: CVE-2020-5233
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-qqxw-m5fj-f7gv
Type: github-advisory

## Affected
- Go: `github.com/oauth2-proxy/oauth2-proxy` — affected >=0 <5.0.0

## Details
### Impact
An open redirect vulnerability has been found in `oauth2_proxy`. Anyone who uses `oauth2_proxy` may potentially be impacted. 

For a context [detectify] have an in depth blog post about the potential impact of an open redirect. Particularly see the OAuth section.

**tl;dr**: People's authentication tokens could be silently harvested by an attacker. e.g:
`facebook.com/oauth.php?clientid=123&state=abc&redirect_url=https://yourdomain.com/red.php?url%3dhttps://attacker.com/`

### Patches

@sauyon found the issue, and has submitted a patch. 

```
diff --git a/oauthproxy.go b/oauthproxy.go
index 72ab580..f420df6 100644
--- a/oauthproxy.go
+++ b/oauthproxy.go
@@ -517,7 +517,7 @@ func (p *OAuthProxy) GetRedirect(req *http.Request) (redirect string, err error)
 // IsValidRedirect checks whether the redirect URL is whitelisted
 func (p *OAuthProxy) IsValidRedirect(redirect string) bool {
 	switch {
-	case strings.HasPrefix(redirect, "/") && !strings.HasPrefix(redirect, "//"):
+	case strings.HasPrefix(redirect, "/") && !strings.HasPrefix(redirect, "//") && !strings.HasPrefix(redirect, "/\\"):
 		return true
 	case strings.HasPrefix(redirect, "http://") || strings.HasPrefix(redirect, "https://"):
 		redirectURL, err := url.Parse(redirect)
```

This patch will be applied to the next release, which is scheduled for when this is publicly disclosed.

### Workarounds

At this stage there is no work around.

## References
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-qqxw-m5fj-f7gv
- https://nvd.nist.gov/vuln/detail/CVE-2020-5233
- https://github.com/oauth2-proxy/oauth2_proxy/commit/a316f8a06f3c0ca2b5fc5fa18a91781b313607b2
- https://blog.detectify.com/2019/05/16/the-real-impact-of-an-open-redirect
- https://github.com/oauth2-proxy/oauth2_proxy/releases/tag/v5.0.0
