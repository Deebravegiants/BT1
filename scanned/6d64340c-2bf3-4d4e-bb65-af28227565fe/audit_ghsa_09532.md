# [H] Flight vulnerable to sensitive information disclosure via default error handler

## Summary
Severity: High
Advisory: GHSA-qrch-52m5-vv85
CVE: CVE-2026-42552
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-qrch-52m5-vv85
Type: github-advisory

## Affected
- Packagist: `flightphp/core` — affected >=0 <3.18.1

## Details
### Summary
The default error handler `Engine::_error()` writes the full exception message, exception code, and stack trace (including absolute filesystem paths) directly into the HTTP 500 response, with no debug gating. Production deployments leak internal paths, any secret interpolated into an exception message, and full module structure — giving attackers primitives for chaining other weaknesses (LFI, path traversal).

### Affected code
`flight/Engine.php` (≈ lines 678-704):

```php
public function _error(Throwable $e): void
{
    ...
    $msg = sprintf(<<<'HTML'
        <h1>500 Internal Server Error</h1>
            <h3>%s (%s)</h3>
            <pre>%s</pre>
        HTML,
        $e->getMessage(),
        $e->getCode(),
        $e->getTraceAsString()
    );
    $this->response()->cache(0)->clearBody()->status(500)->write($msg)->send();
}
```

No `flight.debug` check, no environment gating.

### Proof of concept
Any uncaught exception — including those auto-raised from `handleError()` — returns:

```
HTTP/1.1 500 Internal Server Error

<h1>500 Internal Server Error</h1>
  <h3>secret path /var/www/config/db.yml; token=LEAKED123 (0)</h3>
  <pre>#0 [internal function]: {closure}()
  #1 /home/user/app/vendor/flightphp/core/flight/core/Dispatcher.php(361)...
  #2 /home/user/app/vendor/flightphp/core/flight/Engine.php(...)
  ...
  </pre>
```

Reproduced against the live PoC app at `/poc5/error`.

### Impact
- Disclosure of absolute filesystem paths (primes weaponization of LFI / path-traversal vulnerabilities in the same application).
- Disclosure of secrets (DB credentials, API tokens) when exceptions are constructed with interpolated configuration values.
- Enumeration of installed vendor packages and internal application structure.

### Patch (fixed in `3.18.1`, commit `b8dd23a`)
A new `flight.debug` setting (default `false`) gates the verbose output. In production the handler now emits only `<h1>500 Internal Server Error</h1>`. Developers can set `flight.debug = true` in local environments to restore the full trace output.

### Credit
Discovered by **@Rootingg**.

## References
- https://github.com/flightphp/core/security/advisories/GHSA-qrch-52m5-vv85
- https://nvd.nist.gov/vuln/detail/CVE-2026-42552
- https://github.com/flightphp/core/commit/b8dd23aaa828cb289fa3c84e75b2a3717cab50b0
- https://github.com/flightphp/core
- https://github.com/flightphp/core/releases/tag/v3.18.1
