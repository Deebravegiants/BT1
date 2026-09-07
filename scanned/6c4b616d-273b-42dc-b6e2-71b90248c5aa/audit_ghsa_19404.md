# [M] Stored XSS in Miniflux when opening a broken image due to unescaped ServerError in proxy handler

## Summary
Severity: Medium
Advisory: GHSA-mqqg-xjhj-wfgw
CVE: CVE-2023-27592
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-mqqg-xjhj-wfgw
Type: github-advisory

## Affected
- Go: `miniflux.app/v2` — affected >=2.0.25 <2.0.43

## Details
### Impact

Since [v2.0.25](https://github.com/miniflux/v2/releases/tag/2.0.25), Miniflux will automatically [proxy](https://miniflux.app/docs/configuration.html#proxy-images) images served over HTTP to prevent mixed content errors.

When an outbound request made by the Go HTTP client fails, the `html.ServerError` is [returned](https://github.com/miniflux/v2/blob/b2fd84e0d376a3af6329b9bb2e772ce38a25c31c/ui/proxy.go#L76) unescaped without the expected Content Security Policy [header](https://github.com/miniflux/v2/blob/b2fd84e0d376a3af6329b9bb2e772ce38a25c31c/ui/proxy.go#L90) added to valid responses.

By creating an RSS feed item with the inline description containing an `<img>` tag with a `srcset` attribute pointing to an invalid URL like `http:a<script>alert(1)</script>`, we can coerce the proxy handler into an error condition where the invalid URL is returned unescaped and in full.

This results in JavaScript execution on the Miniflux instance as soon as the user is convinced (e.g. by a message in the alt text) to open the broken image.


An attacker can execute arbitrary JavaScript in the context of a victim Miniflux user when they open a broken image in a crafted RSS feed. This can be used to perform actions on the Miniflux instance as that user and gain administrative access to the Miniflux instance if it is reachable and the victim is an administrator.

### Patches

PR #1746 fixes the problem. Available in Miniflux >= 2.0.43.

### Workarounds

- Disable image proxy (default value is `http-only`).

### References

- https://miniflux.app/docs/configuration.html#proxy-images

## References
- https://github.com/miniflux/v2/security/advisories/GHSA-mqqg-xjhj-wfgw
- https://nvd.nist.gov/vuln/detail/CVE-2023-27592
- https://github.com/miniflux/v2/pull/1746
- https://github.com/miniflux/v2
- https://github.com/miniflux/v2/blob/b2fd84e0d376a3af6329b9bb2e772ce38a25c31c/ui/proxy.go#L76
- https://github.com/miniflux/v2/blob/b2fd84e0d376a3af6329b9bb2e772ce38a25c31c/ui/proxy.go#L90
- https://github.com/miniflux/v2/releases/tag/2.0.25
- https://github.com/miniflux/v2/releases/tag/2.0.43
- https://miniflux.app/docs/configuration.html#proxy-images
