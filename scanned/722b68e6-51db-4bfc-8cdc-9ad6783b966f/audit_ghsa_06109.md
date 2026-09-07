# [M] WebOb: Open redirect in Location header normalization via leading C0 control / space characters

## Summary
Severity: Medium
Advisory: GHSA-6hx8-3wjj-gr8g
CVE: CVE-2026-54770
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-6hx8-3wjj-gr8g
Type: github-advisory

## Affected
- PyPI: `webob` — affected >=0 <1.8.11

## Details
## Summary

This is a third follow-up to **CVE-2024-42353 / GHSA-mg3v-6m49-jhp3**
and **CVE-2026-44889 / GHSA-fh3h-vg37-cc95**.

WebOb makes the `Location` header absolute when it serves a redirect. To stop a
relative or protocol-relative target from redirecting users off-host, it checks
the value for a URI scheme and for a leading `//`, then joins it against the
request URI with `urllib.parse.urljoin()`. The previous fix additionally stripped
ASCII tab/CR/LF from the value before those checks.

However, on Python 3.10+ `urllib.parse.urljoin()` (via `urlsplit()`) does more
than remove tab/CR/LF: **it also strips leading and trailing C0 control
characters (`U+0000`–`U+001F`) and spaces from the URL before parsing it.**
Because WebOb's guard checks (`SCHEME_RE` and `startswith("//")`) run against the
*un-stripped* value, a single leading space or control byte slips past them, and
`urljoin()` then silently removes that byte and parses what remains as a
protocol-relative — or even absolute — URL. The result is an open redirect to an
attacker-controlled host.

## Details

`Response._make_location_absolute()` (in `src/webob/response.py`) performed,
prior to the fix:

```python
value = value.replace("\t", "").replace("\r", "").replace("\n", "")

if SCHEME_RE.search(value):          # ^[a-z]+:   -> already absolute, return as-is
    return value

if value.startswith("//"):           # neutralize protocol-relative URLs
    value = f"/%2f{value[2:]}"

new_location = urlparse.urljoin(_request_uri(environ), value)
```

Consider the Location value `" //www.example.com/test"` (a single leading space):

1. The explicit strip only removes `\t`, `\r`, `\n` — the leading **space**
   survives.
2. `SCHEME_RE` (`^[a-z]+:`) does **not** match — the value starts with a space.
3. `value.startswith("//")` is **False** — the value starts with a space, not
   `/`. The `//` → `/%2f` neutralization is skipped.
4. `urllib.parse.urljoin(_request_uri(environ), " //www.example.com/test")` then
   **strips the leading space** before parsing, sees `//www.example.com/test`,
   treats it as protocol-relative, and returns
   `http://www.example.com/test`.

The same bypass works with a value such as `" https://www.example.com/test"`
(leading space + a full scheme): `SCHEME_RE` does not match the space-prefixed
string, but `urljoin()` strips the space and returns the fully absolute
attacker URL `https://www.example.com/test`.

Any C0 control character works equally well in place of the space, e.g.
`"\x00//www.example.com/test"` or `"\x1f//www.example.com/test"`, because
`urlsplit()` strips the whole leading C0-control-and-space run.

### Affected entry points

- **`Response.location`** — any application that sets a relative/attacker-influenced
  `Location` and serves the response (the classic redirect path).
- **`Request.relative_url()`** — used `urllib.parse.urljoin()` directly and was
  subject to the same character stripping.
- **`webob.exc._HTTPMove` subclasses** (`HTTPMovedPermanently`, `HTTPFound`,
  `HTTPSeeOther`, `HTTPTemporaryRedirect`, `HTTPPermanentRedirect`, etc.) — these
  built their absolute Location with `urlparse.urljoin(req.path_url, self.location)`
  **without** going through `_make_location_absolute()` at all, so they bypassed
  even the tab/CR/LF strip and the `//` → `/%2f` neutralization. A protocol-relative
  location passed to e.g. `HTTPFound(location="//evil.example")` redirected off-host.

## Proof of Concept

```python
from webob import Response
from webob.request import Request

res = Response()
res.status = "301"
res.location = " //www.example.com/test"   # note the single leading space

req = Request.blank("/")                    # request host is "localhost"
print(req.get_response(res).location)
# Vulnerable (<= 1.8.10):  http://www.example.com/test   <-- open redirect
# Fixed:                   http://localhost/ //www.example.com/test
```

Absolute-URL variant:

```python
res.location = " https://www.example.com/test"
# Vulnerable: https://www.example.com/test   <-- off-host
# Fixed:      http://localhost/ https://www.example.com/test
```

Via the HTTP exceptions:

```python
from webob import exc

environ = {
    "wsgi.url_scheme": "http", "SERVER_NAME": "localhost",
    "SERVER_PORT": "80", "REQUEST_METHOD": "HEAD", "PATH_INFO": "/",
}
m = exc.HTTPFound(location="//www.example.com/test")
m(environ, lambda *a, **k: None)
print(m.location)
# Vulnerable: //www.example.com/test          <-- open redirect
# Fixed:      http://localhost/%2fwww.example.com/test
```

## Impact

An unauthenticated remote attacker who controls (in whole or part) the redirect
target of an application built on WebOb can redirect a user from a trusted host to
an attacker-controlled host. This enables phishing and credential-theft campaigns
that abuse the trusted origin, and can be chained with OAuth/SSO `redirect_uri`
flows to leak tokens. Exploitation requires user interaction (following the
redirect). Confidentiality and integrity impact are limited (`L`); the scope is
changed (`C`) because the trust boundary of the originating site is crossed.

## Patches

Fixed by replacing the use of `urllib.parse.urljoin()` with WebOb's own
RFC 3986 reference-resolution implementation, `webob.util.urljoin()`, which
resolves the reference **exactly as given, character for character, with no
whitespace or control-character removal**.

- `Response._make_location_absolute()` now uses `webob.util.urljoin()`.
- `Request.relative_url()` now uses `webob.util.urljoin()`.
- `webob.exc._HTTPMove` now normalizes its Location through the same
  `_make_location_absolute()` code path as `Response`, so protocol-relative and
  whitespace-smuggled locations are neutralized there too.

Users should upgrade to the patched release. There are no API changes.

## Workarounds

- Only ever set the `Location` header / redirect target to a fully-qualified URI
  whose host you control, or strictly allowlist redirect destinations before
  handing them to WebOb.
- Reject any redirect target that does not begin with `https://yourhost/` (or a
  validated relative path with no leading whitespace/control bytes).

## References

- This advisory: GHSA-6hx8-3wjj-gr8g
- GHSA-fh3h-vg37-cc95 (CVE-2026-44889) — second incomplete fix (tab/CR/LF)
- GHSA-mg3v-6m49-jhp3 (CVE-2024-42353) — original open redirect fix
- RFC 3986, Section 5 — Reference Resolution: https://www.rfc-editor.org/rfc/rfc3986#section-5
- Python `urllib.parse` URL stripping behavior (CPython 3.10+, removal of leading
  and trailing C0 control and space characters): https://docs.python.org/3/library/urllib.parse.html
  
To report a vulnerability to the Pylons Project please take a look at:

 - Pylons Project security policy and reporting process:
  https://github.com/Pylons/.github/blob/main/SECURITY.md
- Security contact (private, coordinated disclosure): `pylons-project-security@googlegroups.com`
  (the Pylons Project requests a 90-day disclosure embargo)

## Credit

Reported via the Pylons Project security mailing list by:

- **tonghuaroot** — for the residual open redirect in
  `Response._make_location_absolute()`: the 1.8.10 fix stripped only ASCII
  tab/CR/LF, but `urllib.parse.urljoin()` also strips leading C0 control and
  space characters, so values such as `" //attacker.example/path"` (and
  `" https://attacker.example/path"`) still escaped off-host.
- **Matheus Polkorny** — for identifying that the `webob.exc._HTTPMove`
  redirect exceptions (`HTTPFound` and friends) performed their own
  `urllib.parse.urljoin()` normalization and never went through
  `_make_location_absolute()`, so a protocol-relative location such as
  `//evil.example/path/` redirected off-host through that separate code path.

## References
- https://github.com/Pylons/webob/security/advisories/GHSA-6hx8-3wjj-gr8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-54770
- https://github.com/Pylons/webob/commit/ff89560643fb252751b4db8806a283b5377f1f07
- https://github.com/Pylons/webob
- https://github.com/Pylons/webob/tree/1.8.11
