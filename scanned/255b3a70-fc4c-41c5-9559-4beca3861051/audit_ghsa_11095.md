# [H] Scriban has Uncontrolled Recursion in `object.to_json` Causing Unrecoverable Process Crash via StackOverflowException

## Summary
Severity: High
Advisory: GHSA-xcx6-vp38-8hr5
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-xcx6-vp38-8hr5
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

The `object.to_json` builtin function in Scriban performs recursive JSON serialization via an internal `WriteValue()` static local function that has no depth limit, no circular reference detection, and no stack overflow guard. A Scriban template containing a self-referencing object passed to `object.to_json` triggers unbounded recursion, causing a `StackOverflowException` that terminates the hosting .NET process. This is a fatal, unrecoverable crash — `StackOverflowException` cannot be caught by user code in .NET.

## Details

The vulnerable code is the `WriteValue()` static local function at `src/Scriban/Functions/ObjectFunctions.cs:494`:

```csharp
static void WriteValue(TemplateContext context, Utf8JsonWriter writer, object value)
{
    var type = value?.GetType() ?? typeof(object);
    if (value is null || value is string || value is bool ||
        type.IsPrimitiveOrDecimal() || value is IFormattable)
    {
        JsonSerializer.Serialize(writer, value, type);
    }
    else if (value is IList || type.IsArray) {
        writer.WriteStartArray();
        foreach (var x in context.ToList(context.CurrentSpan, value))
        {
            WriteValue(context, writer, x);  // recursive, no depth check
        }
        writer.WriteEndArray();
    }
    else {
        writer.WriteStartObject();
        var accessor = context.GetMemberAccessor(value);
        foreach (var member in accessor.GetMembers(context, context.CurrentSpan, value))
        {
            if (accessor.TryGetValue(context, context.CurrentSpan, value, member, out var memberValue))
            {
                writer.WritePropertyName(member);
                WriteValue(context, writer, memberValue);  // recursive, no depth check
            }
        }
        writer.WriteEndObject();
    }
}
```

This function has **none** of the safety mechanisms present in other recursive paths:

- `ObjectToString()` at `TemplateContext.Helpers.cs:98` checks `ObjectRecursionLimit` (default 20)
- `EnterRecursive()` at `TemplateContext.cs:957` calls `RuntimeHelpers.EnsureSufficientExecutionStack()`
- `CheckAbort()` at `TemplateContext.cs:464` also calls `EnsureSufficientExecutionStack()`

The `WriteValue()` function bypasses all of these because it is a static local function that only takes the `TemplateContext` for member access — it never calls `EnterRecursive()`, never checks `ObjectRecursionLimit`, and never calls `EnsureSufficientExecutionStack()`.

**Execution flow:**

1. Template creates a ScriptObject: `{{ x = {} }}`
2. Sets a self-reference: `x.self = x` — stores a reference in `ScriptObject.Store` dictionary
3. Pipes to `object.to_json`: `x | object.to_json` → calls `ToJson()` at line 477
4. `ToJson()` calls `WriteValue(context, writer, value)` at line 488
5. `WriteValue` enters the `else` branch (line 515), gets members via accessor, finds "self"
6. `TryGetValue` returns `x` itself, `WriteValue` recurses with the same object — infinite loop
7. `StackOverflowException` is thrown — **fatal, cannot be caught, process terminates**

## PoC

```scriban
{{ x = {}; x.self = x; x | object.to_json }}
```

In a hosting application:

```csharp
using Scriban;

// This will crash the entire process with StackOverflowException
var template = Template.Parse("{{ x = {}; x.self = x; x | object.to_json }}");
var result = template.Render(); // FATAL: process terminates here
```

Even without circular references, deeply nested objects can exhaust the stack since no depth limit is enforced:

```scriban
{{ a = {}
   b = {inner: a}
   c = {inner: b}
   d = {inner: c}
   # ... continue nesting ...
   result = deepest | object.to_json }}
```

## Impact

- **Process crash DoS**: Any application embedding Scriban for user-provided templates (CMS platforms, email template engines, report generators, static site generators) can be crashed by a single malicious template. The crash is unrecoverable — `StackOverflowException` terminates the .NET process.
- **No try/catch protection possible**: Unlike most exceptions, `StackOverflowException` cannot be caught by application code. The hosting application cannot wrap `template.Render()` in a try/catch to survive this.
- **No authentication required**: `object.to_json` is a default builtin function (registered in `BuiltinFunctions.cs`), available in all Scriban templates unless explicitly removed.
- **Trivial to exploit**: The PoC is a single line of template code.

## Recommended Fix

Add a depth counter parameter to `WriteValue()` and check it against `ObjectRecursionLimit`, consistent with how `ObjectToString` is protected. Also add `EnsureSufficientExecutionStack()` as a safety net:

```csharp
static void WriteValue(TemplateContext context, Utf8JsonWriter writer, object value, int depth = 0)
{
    if (context.ObjectRecursionLimit != 0 && depth > context.ObjectRecursionLimit)
    {
        throw new ScriptRuntimeException(context.CurrentSpan,
            $"Exceeding object recursion limit `{context.ObjectRecursionLimit}` in object.to_json");
    }

    try
    {
        RuntimeHelpers.EnsureSufficientExecutionStack();
    }
    catch (InsufficientExecutionStackException)
    {
        throw new ScriptRuntimeException(context.CurrentSpan,
            "Exceeding recursive depth limit in object.to_json, near to stack overflow");
    }

    var type = value?.GetType() ?? typeof(object);
    if (value is null || value is string || value is bool ||
        type.IsPrimitiveOrDecimal() || value is IFormattable)
    {
        JsonSerializer.Serialize(writer, value, type);
    }
    else if (value is IList || type.IsArray) {
        writer.WriteStartArray();
        foreach (var x in context.ToList(context.CurrentSpan, value))
        {
            WriteValue(context, writer, x, depth + 1);
        }
        writer.WriteEndArray();
    }
    else {
        writer.WriteStartObject();
        var accessor = context.GetMemberAccessor(value);
        foreach (var member in accessor.GetMembers(context, context.CurrentSpan, value))
        {
            if (accessor.TryGetValue(context, context.CurrentSpan, value, member, out var memberValue))
            {
                writer.WritePropertyName(member);
                WriteValue(context, writer, memberValue, depth + 1);
            }
        }
        writer.WriteEndObject();
    }
}
```

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-xcx6-vp38-8hr5
- https://github.com/scriban/scriban
