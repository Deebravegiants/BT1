# [H] Scriban has an authorization bypass due to stale include cache surviving TemplateContext.Reset() 

## Summary
Severity: High
Advisory: GHSA-x6m9-38vm-2xhf
CWE: CWE-226
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-x6m9-38vm-2xhf
Type: github-advisory

## Affected
- NuGet: `scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

`TemplateContext.Reset()` claims that a `TemplateContext` can be reused safely on the same thread, but it does not clear `CachedTemplates`. If an application pools `TemplateContext` objects and uses an `ITemplateLoader` that resolves content per request, tenant, or user, a previously authorized include can be served to later renders without calling `TemplateLoader.Load()` again.

## Details

The relevant code path is:

- `TemplateContext.Reset()` only clears output, globals, cultures, and source files in `src/Scriban/TemplateContext.cs` lines 877–902.
- `CachedTemplates` is initialized once and kept on the context in `src/Scriban/TemplateContext.cs` line 197.
- `include` resolves templates through `IncludeFunction.Invoke()` in `src/Scriban/Functions/IncludeFunction.cs` lines 29–43.
- `IncludeFunction.Invoke()` calls `TemplateContext.GetOrCreateTemplate()` in `src/Scriban/TemplateContext.cs` lines 1249–1256.
- If a template path is already present in `CachedTemplates`, Scriban returns the cached compiled template and does **not** call `TemplateLoader.Load()` again.

This becomes a security issue when `ITemplateLoader.Load()` returns request-dependent content. A first render can prime the cache with an admin-only or tenant-specific template, and later renders on the same reused `TemplateContext` will receive that stale template even after `Reset()`.

---

## Proof of Concept

### Setup

```bash
mkdir scriban-poc1
cd scriban-poc1
dotnet new console --framework net8.0
dotnet add package Scriban --version 6.6.0
```

### `Program.cs`

```csharp
using Scriban;
using Scriban.Parsing;
using Scriban.Runtime;

var loader = new SwitchingLoader();
var context = new TemplateContext
{
    TemplateLoader = loader,
};

var template = Template.Parse("{{ include 'profile' }}");

loader.Content = "admin-only";
Console.WriteLine("first=" + template.Render(context));

context.Reset();

loader.Content = "guest-view";
Console.WriteLine("second=" + template.Render(context));

sealed class SwitchingLoader : ITemplateLoader
{
    public string Content { get; set; } = string.Empty;

    public string GetPath(TemplateContext context, SourceSpan callerSpan, string templateName) => templateName;

    public string Load(TemplateContext context, SourceSpan callerSpan, string templatePath) => Content;

    public ValueTask<string> LoadAsync(TemplateContext context, SourceSpan callerSpan, string templatePath)
        => new(Content);
}
```

### Run

```bash
dotnet run
```

### Actual Output

```
first=admin-only
second=admin-only
```

### Expected Output

```
first=admin-only
second=guest-view
```

The second render should reload the template after `Reset()`, but it instead reuses the cached compiled template from the previous render.

---

## Impact

This is a cross-render data isolation issue. Any application that reuses `TemplateContext` objects and uses a request-dependent `ITemplateLoader` can leak previously authorized template content across requests, users, or tenants.

The issue impacts applications that:

- Pool or reuse `TemplateContext`
- Call `Reset()` between requests
- Use `include`
- Resolve include content based on request-specific state

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-x6m9-38vm-2xhf
- https://github.com/scriban/scriban
