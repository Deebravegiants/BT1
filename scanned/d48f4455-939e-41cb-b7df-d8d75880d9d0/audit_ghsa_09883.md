# [M] Saltcorn: Open Redirect in `POST /auth/login` due to incomplete `is_relative_url` validation (backslash bypass)

## Summary
Severity: Medium
Advisory: GHSA-f3g8-9xv5-77gv
CVE: CVE-2026-42259
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-f3g8-9xv5-77gv
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.4.6
- npm: `@saltcorn/server` — affected >=1.5.0-beta.0 <1.5.6
- npm: `@saltcorn/server` — affected >=1.6.0-alpha.0 <1.6.0-beta.5

## Details
### Summary
Saltcorn validates the post-login `dest` parameter with a string check that only blocks `:/` and `//`. Because all WHATWG-compliant browsers normalise backslashes (`\`) to forward slashes (`/`) for special schemes, a payload such as `/\evil.com/path` slips through `is_relative_url()`, is emitted unchanged in the HTTP `Location` header, and causes the browser to navigate cross-origin to an attacker-controlled domain. The bug is reachable on a default install and only requires a victim who can be tricked into logging in via a crafted Saltcorn URL.

### Details
Vulnerable function: `packages/server/routes/utils.js:393-395`

```js
const is_relative_url = (url) => {
  return typeof url === "string" && !url.includes(":/") && !url.includes("//");
};
```

The function's intent is to allow only same-origin redirects, but the allow-list only checks for two literal substrings. It does not handle:
- backslash characters, which WHATWG URL parsing (used by every modern browser) treats as forward slashes for the special schemes `http`, `https`, `ftp`, `ws`, `wss`. A URL parser fed `/\evil.com/path` with a base of `http://victim/` resolves to `http://evil.com/path`.
- non-`http(s):` schemes that do not contain `:/`. The strings `javascript:alert(1)`, `data:text/html,...`, `vbscript:...` all pass.

Vulnerable callsite: `packages/server/auth/routes.js:1371-1376`

```js
} else if (
  (req.body || {}).dest &&
  is_relative_url(decodeURIComponent((req.body || {}).dest))
) {
  res.redirect(decodeURIComponent((req.body || {}).dest));
} else res.redirect("/");
```

The body's `dest` is URL-decoded twice (once by body-parser, once by the explicit `decodeURIComponent`) and the same value is passed to `res.redirect`. Express 5's `res.redirect` runs the value through `encodeurl@2.0.0`, whose whitelist character class `[^\x21\x23-\x3B\x3D\x3F-\x5F\x61-\x7A\x7C\x7E]` includes `\x5C` (backslash). The backslash is therefore not percent-encoded and ends up verbatim in the `Location` response header.

### PoC
[poc.zip](https://github.com/user-attachments/files/26678853/poc.zip)

Please extract the uploaded compressed file before proceeding
1. ./setup.sh
2. ./poc.sh

<img width="419" height="71" alt="스크린샷 2026-04-13 오후 11 44 36" src="https://github.com/user-attachments/assets/9c919ed4-167b-47e3-9873-733f97b44bf0" />

### Impact
Any user who can be lured into clicking a Saltcorn login URL crafted by the attacker will, after submitting their valid credentials, be redirected to an attacker-controlled origin. The redirect happens under the trusted Saltcorn domain, so the user has no visual cue that they are about to leave the site. Realistic abuse patterns:

- Credential phishing — the attacker's site renders a forged "session expired, please log in again" prompt to capture the password the user just typed.

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-f3g8-9xv5-77gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42259
- https://github.com/saltcorn/saltcorn
