# [H] Flight: HTTP method override enabled by default, facilitating CSRF escalation and middleware bypass

## Summary
Severity: High
Advisory: GHSA-vxrr-w42w-w76g
CVE: CVE-2026-42551
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-vxrr-w42w-w76g
Type: github-advisory

## Affected
- Packagist: `flightphp/core` — affected >=0 <3.18.1

## Details
### Summary
`Request::getMethod()` unconditionally honors the `X-HTTP-Method-Override` header and the `$_REQUEST['_method']` parameter on **any** HTTP verb (including safe verbs such as GET), with no opt-in and no whitelist of permitted target methods. A GET request can silently become a DELETE or PUT, enabling CSRF escalation against destructive endpoints, bypass of middleware gated on unsafe verbs, and cache poisoning between CDN and origin.

### Affected code
`flight/net/Request.php` (≈ lines 281-292):

```php
public static function getMethod(): string
{
    $method = self::getVar('REQUEST_METHOD', 'GET');
    if (self::getVar('HTTP_X_HTTP_METHOD_OVERRIDE') !== '') {
        $method = self::getVar('HTTP_X_HTTP_METHOD_OVERRIDE');
    } elseif (isset($_REQUEST['_method']) === true) {
        $method = $_REQUEST['_method'];
    }
    return strtoupper($method);
}
```

`$_REQUEST` aggregates `$_GET` and `$_POST`; on PHP runtimes with `request_order=GPC` it also includes `$_COOKIE`.

### Proof of concept
```
GET /item/42?_method=DELETE        HTTP/1.1
```
is dispatched as `DELETE /item/42`.

```
GET /item/42                       HTTP/1.1
X-HTTP-Method-Override: DELETE
```
is also dispatched as `DELETE /item/42`.

Trivial CSRF vector (no JavaScript required):
```html
<img src="https://victim.tld/item/42?_method=DELETE">
```
loaded on any attacker-controlled page triggers the destructive DELETE on page load, bypassing Same-Origin Policy (image loads are not blocked).

Reproduced against `/poc4/item/42`.

### Impact
- GET → DELETE / PUT CSRF on any route registered for unsafe verbs.
- Bypass of authentication, CSRF token, or rate-limiting middleware that is gated only on POST/DELETE.
- CDN cache poisoning: the CDN caches the GET response body while the origin executed a DELETE.

### Patch (fixed in `3.18.1`, commit `b8dd23a`)
A new `flight.allow_method_override` setting controls both override vectors. Operators can set it to `false` to disable `X-HTTP-Method-Override` and `_method` entirely.

### Credit
Discovered by **@Rootingg**.

## References
- https://github.com/flightphp/core/security/advisories/GHSA-vxrr-w42w-w76g
- https://nvd.nist.gov/vuln/detail/CVE-2026-42551
- https://github.com/flightphp/core/commit/b8dd23aaa828cb289fa3c84e75b2a3717cab50b0
- https://github.com/flightphp/core
- https://github.com/flightphp/core/releases/tag/v3.18.1
