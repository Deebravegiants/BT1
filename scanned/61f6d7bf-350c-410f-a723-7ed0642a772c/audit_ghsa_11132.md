# [M] Scriban Affected by Memory Exhaustion (OOM) via Unbounded String Generation (Denial of Service)

## Summary
Severity: Medium
Advisory: GHSA-5rpf-x9jg-8j5p
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-5rpf-x9jg-8j5p
Type: github-advisory

## Affected
- NuGet: `scriban` — affected >=0 <6.6.0
- NuGet: `Scriban.Signed` — affected >=0 <6.6.0

## Details
`TemplateContext.LimitToString` defaults to `0` (unlimited). While Scriban implements a default `LoopLimit` of 1000, an attacker can still cause massive memory allocation via exponential string growth. Doubling a string for just 30 iterations generates over 1GB of text, instantly exhausting heap memory and crashing the host process. Because no output size limit is enforced, repeated string concatenation results in exponential memory growth.

**Proof of Concept (PoC):**
The following payload executes in under 30 iterations but results in ~1GB string allocation, crashing the process.

```csharp
using Scriban;

string maliciousTemplate =
    @"
        {{
            a = ""A""
            for i in 1..30
                a = a + a
            end
            a
        }}";

var template = Template.Parse(maliciousTemplate);

var context = new TemplateContext();

try
{
    template.Render(context);
}
catch (Exception ex)
{
    Console.WriteLine("\nException: " + ex.Message);
}
```

**Impact:**
An attacker can supply a small template that triggers exponential string growth, forcing the application to allocate excessive memory. This leads to severe memory pressure, garbage collection thrashing, and eventual process termination (DoS).

**Suggested Fix:**
Enforce a sensible default limit for string output. Set default `LimitToString` to 1MB (1,048,576 characters). 

```csharp
public int LimitToString { get; set; } = 1048576; 
```

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-5rpf-x9jg-8j5p
- https://github.com/scriban/scriban/commit/a6fe6074199e5c04f4d29dc8d8e652b24d33e3e4
- https://github.com/scriban/scriban
