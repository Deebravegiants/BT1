# [M] Astros's duplicate trailing slash feature leads to an open redirection security issue

## Summary
Severity: Medium
Advisory: GHSA-cq8c-xv66-36gw
CVE: CVE-2025-54793
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N/E:P (CVSS_V4)
Published: 2025-08-07
Source: https://github.com/advisories/GHSA-cq8c-xv66-36gw
Type: github-advisory

## Affected
- npm: `astro` — affected >=5.2.0 <5.12.8

## Details
## Summary

There is an Open Redirection vulnerability in the trailing slash redirection logic when handling paths with double slashes. This allows an attacker to redirect users to arbitrary external domains by crafting URLs such as `https://mydomain.com//malicious-site.com/`. This increases the risk of phishing and other social engineering attacks.

This affects Astro >=5.2.0 sites that use on-demand rendering (SSR) with the Node or Cloudflare adapter. It does not affect static sites, or sites deployed to Netlify or Vercel.

## Background

Astro performs automatic redirection to the canonical URL, either adding or removing trailing slashes according to the value of the [`trailingSlash`](https://docs.astro.build/en/reference/configuration-reference/#trailingslash) configuration option. It follows the following rules:

- If `trailingSlash` is set to `"never"`, `https://example.com/page/` will redirect to `https://example.com/page` 
- If `trailingSlash` is set to `"always"`, `https://example.com/page` will redirect to `https://example.com/page/`

It also collapses multiple trailing slashes, according to the following rules:

- If `trailingSlash` is set to `"always"` or `"ignore"` (the default), `https://example.com/page//` will redirect to `https://example.com/page/`
- If `trailingSlash` is set to `"never"`, `https://example.com/page//` will redirect to `https://example.com/page` 

It does this by returning a `301` redirect to the target path. The vulnerability occurs because it uses a relative path for the redirect. To redirect from `https://example.com/page` to `https://example.com/page/`, it sending a 301 response with the header `Location: /page/`. The browser resolves this URL relative to the original page URL and redirects to `https://example.com/page/`

## Details

The vulnerability occurs if the target path starts with `//`. A request for `https://example.com//page` will send the header `Location: //page/`. The browser interprets this as a [protocol-relative URL](https://en.wikipedia.org/wiki/URL#Protocol-relative_URLs), so instead of redirecting to `https://example.com//page/`, it will attempt to redirect to `https://page/`. This is unlikely to resolve, but by crafting a URL in the form `https://example.com//target.domain/subpath`, it will send the header `Location: //target.domain/subpath/`, which the browser translates as a redirect to `https://target.domain/subpath/`. The subpath part is required because otherwise Astro will interpret `/target.domain` as a file download, which skips trailing slash handling.

This leads to an [Open Redirect](https://cwe.mitre.org/data/definitions/601.html) vulnerability.

The URL needed to trigger the vulnerability varies according to the `trailingSlash` setting.

- If `trailingSlash` is set to `"never"`, a URL in the form `https://example.com//target.domain/subpath/`
- If `trailingSlash` is set to `"always"`, a URL in the form `https://example.com//target.domain/subpath`
- For any config value, a URL in the form `https://example.com//target.domain/subpath//`

## Impact

This is classified as an Open Redirection vulnerability (CWE-601). It affects any user who clicks on a specially crafted link pointing to the affected domain. Since the domain appears legitimate, victims may be tricked into trusting the redirected page, leading to possible credential theft, malware distribution, or other phishing-related attacks.

No authentication is required to exploit this vulnerability. Any unauthenticated user can trigger the redirect by clicking a malicious link.

## Mitigation

Usrs can test if your site is affected by visiting `https://yoursite.com//docs.astro.build/en//`. If a user is redirected to the Astro docs then their site is affected and must be updated.

Upgrade  to Astro 5.12.8. To mitigate at the network level, block outgoing redirect responses with a `Location` header value that starts with `//`.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-cq8c-xv66-36gw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54793
- https://github.com/withastro/astro/commit/0567fb7b50c0c452be387dd7c7264b96bedab48f
- https://github.com/withastro/astro
