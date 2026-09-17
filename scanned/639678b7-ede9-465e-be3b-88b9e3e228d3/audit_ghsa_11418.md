# [M] Scriban has Multiple Denial-of-Service Vectors via Unbounded Resource Consumption During Expression Evaluation

## Summary
Severity: Medium
Advisory: GHSA-xw6w-9jjh-p9cr
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-xw6w-9jjh-p9cr
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

Scriban's expression evaluation contains three distinct code paths that allow an attacker who can supply a template to cause denial of service through unbounded memory allocation or CPU exhaustion. The existing safety controls (`LimitToString`, `LoopLimit`) do not protect these paths, giving applications a false sense of safety when evaluating untrusted templates.

## Details

### Vector 1: Unbounded string multiplication

In `ScriptBinaryExpression.cs`, the `CalculateToString` method handles the `string * int` operator by looping without any upper bound:

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs:319-334
var leftText = context.ObjectToString(left);
var builder = new StringBuilder();
for (int i = 0; i < value; i++)
{
    builder.Append(leftText);
}
return builder.ToString();
```

The `LimitToString` safety control (default 1MB) does **not** protect this code path. It only applies to `ObjectToString` output conversions in `TemplateContext.Helpers.cs` (lines 101-121), not to intermediate string values constructed inside `CalculateToString`. The `LoopLimit` also does not apply because this is a C# `for` loop, not a template-level loop — `StepLoop()` is never called here.

### Vector 2: Unbounded BigInteger shift left

The `CalculateLongWithInt` and `CalculateBigIntegerNoFit` methods handle `ShiftLeft` without any bound on the shift amount:

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs:710-711
case ScriptBinaryOperator.ShiftLeft:
    return (BigInteger)left << (int)right;
```

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs:783-784
case ScriptBinaryOperator.ShiftLeft:
    return left << (int)right;
```

In contrast, the `Power` operator at lines 722 and 795 uses `BigInteger.ModPow(left, right, MaxBigInteger)` to cap results. The `MaxBigInteger` constant (`BigInteger.One << 1024 * 1024`, defined at line 690) already exists but is never applied to shift operations.

### Vector 3: LoopLimit bypass via range enumeration in builtin functions

The range operators `..` and `..<` produce lazy `IEnumerable<object>` iterators:

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs:401-417
private static IEnumerable<object> RangeInclude(BigInteger left, BigInteger right)
{
    if (left < right)
    {
        for (var i = left; i <= right; i++)
        {
            yield return FitToBestInteger(i);
        }
    }
    // ...
}
```

When these ranges are consumed by builtin functions, `LoopLimit` is completely bypassed because `StepLoop()` is only called in `ScriptForStatement` and `ScriptWhileStatement` — it is never called in any function under `src/Scriban/Functions/`. For example:

- `ArrayFunctions.Size` (line 609) calls `.Cast<object>().Count()`, fully enumerating the range
- `ArrayFunctions.Join` (line 388) iterates with `foreach` and appends to a `StringBuilder` with no size limit

## PoC

### Vector 1 — String multiplication OOM:
```csharp
var template = Template.Parse("{{ 'AAAA' * 500000000 }}");
var context = new TemplateContext();
// context.LimitToString is 1048576 by default — does NOT protect this path
template.Render(context); // OutOfMemoryException: attempts ~2GB allocation
```

### Vector 2 — BigInteger shift OOM:
```csharp
var template = Template.Parse("{{ 1 << 100000000 }}");
var context = new TemplateContext();
template.Render(context); // Allocates BigInteger with 100M bits (~12.5MB)
// {{ 1 << 2000000000 }} attempts ~250MB
```

### Vector 3 — LoopLimit bypass via range + builtin:
```csharp
var template = Template.Parse("{{ (0..1000000000) | array.size }}");
var context = new TemplateContext();
// context.LoopLimit is 1000 — does NOT protect builtin function iteration
template.Render(context); // CPU exhaustion: enumerates 1 billion items
```

```csharp
var template = Template.Parse("{{ (0..10000000) | array.join ',' }}");
var context = new TemplateContext();
template.Render(context); // Memory exhaustion: builds ~80MB+ joined string
```

## Impact

An attacker who can supply a Scriban template (common in CMS platforms, email templating systems, reporting tools, and other applications embedding Scriban) can cause denial of service by crashing the host process via `OutOfMemoryException` or exhausting CPU resources. This is particularly impactful because:

1. Applications relying on the default safety controls (`LoopLimit=1000`, `LimitToString=1MB`) believe they are protected against resource exhaustion from untrusted templates, but these controls have gaps.
2. A single malicious template expression is sufficient — no complex template logic is required.
3. The `OutOfMemoryException` in vectors 1 and 2 typically terminates the entire process, not just the template evaluation.

## Recommended Fix

### Vector 1 — String multiplication: Check `LimitToString` before the loop

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs, before line 330
var leftText = context.ObjectToString(left);
if (context.LimitToString > 0 && (long)value * leftText.Length > context.LimitToString)
{
    throw new ScriptRuntimeException(span,
        $"String multiplication would exceed LimitToString ({context.LimitToString} characters)");
}
var builder = new StringBuilder();
for (int i = 0; i < value; i++)
```

### Vector 2 — BigInteger shift: Cap the shift amount

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs, lines 710-711 and 783-784
case ScriptBinaryOperator.ShiftLeft:
    if (right > 1048576) // Same as MaxBigInteger bit count
        throw new ScriptRuntimeException(span,
            $"Shift amount {right} exceeds maximum allowed (1048576)");
    return (BigInteger)left << (int)right;
```

### Vector 3 — Range + builtins: Add iteration counting to range iterators

Pass `TemplateContext` to `RangeInclude`/`RangeExclude` and enforce a limit:

```csharp
private static IEnumerable<object> RangeInclude(TemplateContext context, BigInteger left, BigInteger right)
{
    var maxRange = context.LoopLimit > 0 ? context.LoopLimit : int.MaxValue;
    int count = 0;
    if (left < right)
    {
        for (var i = left; i <= right; i++)
        {
            if (++count > maxRange)
                throw new ScriptRuntimeException(context.CurrentNode.Span,
                    $"Range enumeration exceeds LoopLimit ({maxRange})");
            yield return FitToBestInteger(i);
        }
    }
    // ... same for descending branch
}
```

Alternatively, validate range size eagerly at creation time: `if (BigInteger.Abs(right - left) > maxRange) throw ...`

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-xw6w-9jjh-p9cr
- https://github.com/scriban/scriban
