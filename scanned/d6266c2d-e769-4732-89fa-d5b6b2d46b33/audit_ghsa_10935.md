# [M] Scriban: Denial of Service via Unbounded Cumulative Template Output Bypassing LimitToString

## Summary
Severity: Medium
Advisory: GHSA-m2p3-hwv5-xpqw
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-m2p3-hwv5-xpqw
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

The `LimitToString` safety limit (default 1MB since commit `b5ac4bf`) can be bypassed to allocate approximately 1GB of memory by exploiting the per-call reset of `_currentToStringLength` in `ObjectToString`. Each template expression rendered through `TemplateContext.Write(SourceSpan, object)` triggers a separate top-level `ObjectToString` call that resets the length counter to zero, and the underlying `StringBuilderOutput` has no cumulative output size limit. An attacker who can supply a template can cause an out-of-memory condition in the host application.

## Details

The root cause is in `TemplateContext.Helpers.cs`, in the `ObjectToString` method:

```csharp
// src/Scriban/TemplateContext.Helpers.cs:89-111
public virtual string ObjectToString(object value, bool nested = false)
{
    if (_objectToStringLevel == 0)
    {
        _currentToStringLength = 0;  // <-- resets on every top-level call
    }
    try
    {
        _objectToStringLevel++;
        // ...
        var result = ObjectToStringImpl(value, nested);
        if (LimitToString > 0 && _objectToStringLevel == 1 && result != null && result.Length >= LimitToString)
        {
            return result + "...";
        }
        return result;
    }
    // ...
}
```

Each time a template expression is rendered, `TemplateContext.Write(SourceSpan, object)` calls `ObjectToString`:

```csharp
// src/Scriban/TemplateContext.cs:693-701
public virtual TemplateContext Write(SourceSpan span, object textAsObject)
{
    if (textAsObject != null)
    {
        var text = ObjectToString(textAsObject);  // fresh _currentToStringLength = 0
        Write(text);
    }
    return this;
}
```

The `StringBuilderOutput.Write` method appends unconditionally with no size check:

```csharp
// src/Scriban/Runtime/StringBuilderOutput.cs:47-50
public void Write(string text, int offset, int count)
{
    Builder.Append(text, offset, count);  // no cumulative limit
}
```

**Execution flow:**
1. Template creates a string of length 1,048,575 (one byte under the 1MB `LimitToString` default)
2. A `for` loop iterates up to `LoopLimit` (default 1000) times
3. Each iteration renders the string via `Write(span, x)` → `ObjectToString(x)`
4. `ObjectToString` resets `_currentToStringLength = 0` since `_objectToStringLevel == 0`
5. The string passes the `LimitToString` check (1,048,575 < 1,048,576)
6. Full string is appended to `StringBuilder` — no cumulative tracking
7. After 1000 iterations: ~1GB allocated in-memory

## PoC

```csharp
using Scriban;

// Uses only default TemplateContext settings (LoopLimit=1000, LimitToString=1048576)
var template = Template.Parse("{{ x = \"\" | string.pad_left 1048575 }}{{ for i in 1..1000 }}{{ x }}{{ end }}");
// This will allocate ~1GB in the StringBuilder, likely causing OOM
var result = template.Render();
```

Equivalent Scriban template:
```scriban
{{ x = "" | string.pad_left 1048575 }}{{ for i in 1..1000 }}{{ x }}{{ end }}
```

Each of the 1000 loop iterations outputs a 1,048,575-character string. Each passes the per-call `LimitToString` check independently. Total output: ~1,000,000,000 characters (~1GB) allocated in the `StringBuilder`.

## Impact

- **Denial of Service:** An attacker who can supply Scriban templates (common in CMS, email templating, report generation) can crash the host application via out-of-memory
- **Process-level impact:** OOM kills the entire .NET process, not just the template rendering — affects all concurrent users
- **Bypass of safety mechanism:** The `LimitToString` limit was specifically introduced to prevent resource exhaustion, but the per-call reset makes it ineffective against cumulative abuse
- **Low complexity:** The exploit template is trivial — a single line

## Recommended Fix

Add a cumulative output size counter to `TemplateContext` that tracks total bytes written across all `Write` calls, independent of the per-object `LimitToString`:

```csharp
// In TemplateContext.cs — add new property and field
private long _totalOutputLength;

/// <summary>
/// Gets or sets the maximum total output length in characters. Default is 10485760 (10 MB). 0 means no limit.
/// </summary>
public int OutputLimit { get; set; } = 10485760;

// In TemplateContext.Write(string, int, int) — add check before writing
public TemplateContext Write(string text, int startIndex, int count)
{
    if (text != null)
    {
        if (OutputLimit > 0)
        {
            _totalOutputLength += count;
            if (_totalOutputLength > OutputLimit)
            {
                throw new ScriptRuntimeException(CurrentSpan, 
                    $"The output limit of {OutputLimit} characters was reached.");
            }
        }
        // ... existing indent/write logic
    }
    return this;
}
```

This provides defense-in-depth: `LimitToString` caps individual object serialization, while `OutputLimit` caps total template output.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-m2p3-hwv5-xpqw
- https://github.com/scriban/scriban
