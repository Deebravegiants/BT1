# [M] SymfonyRuntime CVE-2024-50340 Patch Bypass: Web Requests Can Still Set APP_ENV/APP_DEBUG via parse_str/SAPI Argv Mismatch

## Summary
Severity: Medium
Advisory: GHSA-fqc7-9xjw-jrh3
CVE: CVE-2026-47767
CWE: CWE-20, CWE-436, CWE-74
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-fqc7-9xjw-jrh3
Type: github-advisory

## Affected
- Packagist: `symfony/runtime` — affected >=5.4.46 <5.4.52
- Packagist: `symfony/runtime` — affected >=6.4.14 <6.4.40
- Packagist: `symfony/runtime` — affected >=7.1.7 <7.4.12
- Packagist: `symfony/runtime` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=5.4.46 <5.4.52
- Packagist: `symfony/symfony` — affected >=6.4.14 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.1.7 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

CVE-2024-50340 (GHSA-x8vp-gf4q-mw5j) addressed an issue where, with `register_argc_argv=On`, a crafted query string let an unauthenticated GET change the kernel environment and debug flag by feeding `--env`/`--no-debug` through `$_SERVER['argv']`. The fix shipped in `symfony/runtime` 5.4.46 / 6.4.14 / 7.1.7 gated the argv read on `empty($_GET)` as a proxy for "is this a CLI invocation".

That proxy is unsafe: `parse_str()` (which builds `$_GET`) and the web SAPI (which builds `$_SERVER['argv']` from the raw query when `register_argc_argv=On`) do not agree on every input, so an attacker can craft a query that leaves `$_GET` empty while `$_SERVER['argv']` carries the attacker's flags. `SymfonyRuntime::getInput()` then parses them, restoring the exact primitive CVE-2024-50340 was meant to prevent.

Preconditions and impact match the original CVE: web SAPI, `register_argc_argv=On`, app booted through `symfony/runtime`; from an unauthenticated GET an attacker can flip `APP_ENV` and toggle `APP_DEBUG`.

### Resolution

`SymfonyRuntime` now gates the argv read on `isset($_SERVER['QUERY_STRING'])` rather than on `empty($_GET)`. `QUERY_STRING` is the same input the SAPI uses to build argv, so the security check and the thing it protects no longer parse different sources. Worker SAPIs (FrankenPHP / RoadRunner / Swoole) keep working because the runtime constructor runs once at boot when `QUERY_STRING` is unset.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/3228c3806ee511008bea19a95084d460b17e5d25) for branch 5.4.

### Credits

SymfonyRuntime would like to thank 0xEr3n for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-fqc7-9xjw-jrh3
- https://github.com/symfony/symfony
