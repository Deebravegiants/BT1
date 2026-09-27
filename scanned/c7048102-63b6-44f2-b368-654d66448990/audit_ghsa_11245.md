# [C] Scriban: Sandbox escape due to TypedObjectAccessorcache bypassing MemberFilter after TemplateContext reuse

## Summary
Severity: Critical
Advisory: GHSA-5wr9-m6jw-xx44
CWE: CWE-693
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-5wr9-m6jw-xx44
Type: github-advisory

## Affected
- NuGet: `scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

`TemplateContext` caches type accessors by `Type` only, but those accessors are built using the current `MemberFilter` and `MemberRenamer`. When a `TemplateContext` is reused and the filter is tightened for a later render, Scriban still reuses the old accessor and continues exposing members that should now be hidden.

## Details

The relevant code path is:

- `TemplateContext.GetMemberAccessor()` caches accessors in `_memberAccessors` by `Type` in `src/Scriban/TemplateContext.cs` lines 850–863.
- For plain .NET objects, `GetMemberAccessorImpl()` creates a new `TypedObjectAccessor(type, _keyComparer, MemberFilter, MemberRenamer)` in `src/Scriban/TemplateContext.cs` lines 909–939.
- `TypedObjectAccessor` stores the current filter and precomputes the exposed member set in its constructor and `PrepareMembers()` in `src/Scriban/Runtime/Accessors/TypedObjectAccessor.cs` lines 33–40 and 119–179.
- Member access later goes through `ScriptMemberExpression.GetValue()` in `src/Scriban/Syntax/Expressions/ScriptMemberExpression.cs` lines 67–95, which uses the cached accessor.
- `TemplateContext.Reset()` does **not** clear `_memberAccessors` in `src/Scriban/TemplateContext.cs` lines 877–902.

As a result, once a permissive accessor has been created for a given type, changing `TemplateContext.MemberFilter` later does not take effect for that type on the same reused context.

This is especially relevant because the Scriban docs explicitly recommend `TemplateContext.MemberFilter` for indirect .NET object exposure.

---

## Proof of Concept

### Setup

```bash
mkdir scriban-poc2
cd scriban-poc2
dotnet new console --framework net8.0
dotnet add package Scriban --version 6.6.0
```

### `Program.cs`

```csharp
using System.Reflection;
using Scriban;
using Scriban.Runtime;

var template = Template.Parse("{{ model.secret }}");

var context = new TemplateContext
{
    EnableRelaxedMemberAccess = false
};

var globals = new ScriptObject();
globals["model"] = new SensitiveModel();
context.PushGlobal(globals);

context.MemberFilter = _ => true;
Console.WriteLine("first=" + template.Render(context));

context.Reset();

var globals2 = new ScriptObject();
globals2["model"] = new SensitiveModel();
context.PushGlobal(globals2);

context.MemberFilter = member => member.Name == nameof(SensitiveModel.Public);

Console.WriteLine("second=" + template.Render(context));

sealed class SensitiveModel
{
    public string Public => "ok";
    public string Secret => "leaked";
}
```

### Run

```bash
dotnet run
```

### Actual Output

```
first=leaked
second=leaked
```

### Expected Behavior

The second render should fail or stop exposing `Secret`, because the filter only allows `Public` and `EnableRelaxedMemberAccess` is disabled.

This reproduces a direct filter bypass caused by the stale cached accessor.

---

## Impact

This is a protection-mechanism bypass. Applications that use `TemplateContext.MemberFilter` as part of their sandbox or object-exposure policy can unintentionally expose hidden members across requests when they reuse a `TemplateContext`.

The impact includes:

- Unauthorized read access to filtered properties or fields
- Unauthorized writes if the filtered member also has a setter
- Policy bypass across requests, users, or tenants when contexts are pooled

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-5wr9-m6jw-xx44
- https://github.com/scriban/scriban
