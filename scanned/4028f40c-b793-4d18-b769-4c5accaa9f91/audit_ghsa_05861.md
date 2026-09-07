# [C] jmespath.php has CompilerRuntime code injection via unescaped function names

## Summary
Severity: Critical
Advisory: GHSA-pcw8-m77r-2528
CVE: CVE-2026-54133
CWE: CWE-116, CWE-20, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-pcw8-m77r-2528
Type: github-advisory

## Affected
- Packagist: `mtdowling/jmespath.php` — affected >=0 <2.9.1

## Details
## Impact

`mtdowling/jmespath.php` can generate and execute attacker-controlled PHP code when `JmesPath\CompilerRuntime` is used with an attacker-controlled JMESPath expression. The compiler emits parsed JMESPath function names into generated PHP source without sufficient escaping. A crafted expression can cause the generated cache file to contain executable attacker-controlled PHP, which is then loaded by the compiler runtime.

A vulnerable flow is:

1. An application accepts or constructs a JMESPath expression using attacker-controlled input.
2. The expression is evaluated with `JmesPath\CompilerRuntime`, or with `JmesPath\search()` while `JP_PHP_COMPILE` is enabled.
3. The crafted expression uses a non-identifier value where the parser accepts a function callee.
4. The compiler writes that value into generated PHP source without safely escaping it as a PHP string literal.
5. The generated source is written to the compiled-expression cache directory.
6. `CompilerRuntime` loads the generated cache file.
7. The injected PHP executes in the context of the affected application.

In that flow, an attacker can execute arbitrary PHP code with the privileges of the PHP process. The searched data document is not sufficient to exploit this issue by itself; the attacker must be able to influence the JMESPath expression string.

The default runtime used by `JmesPath\search()` is `AstRuntime`, which interprets the parsed expression tree and is not affected unless `JP_PHP_COMPILE` is enabled. Applications are most likely to be affected when they explicitly instantiate `JmesPath\CompilerRuntime`, enable `JP_PHP_COMPILE` as a performance optimization, and allow users to provide JMESPath expressions for filtering, querying, or transforming data.

## Patches

The issue is patched in `2.9.1` and later.

## Workarounds

If you cannot upgrade immediately, disable `JP_PHP_COMPILE` and do not use `JmesPath\CompilerRuntime` with attacker-controlled expressions. Use the default `AstRuntime` for untrusted expressions. Applications that must continue accepting untrusted JMESPath expressions before upgrading should ensure those expressions are never evaluated by the compiler runtime.

## References
- https://github.com/jmespath/jmespath.php/security/advisories/GHSA-pcw8-m77r-2528
- https://nvd.nist.gov/vuln/detail/CVE-2026-54133
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mtdowling/jmespath.php/CVE-2026-54133.yaml
- https://github.com/jmespath/jmespath.php
