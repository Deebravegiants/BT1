# [H] Scriban has an Infinite Recursion during Object Rendering Leads to Stack Overflow and Process Crash (Denial of Service)

## Summary
Severity: High
Advisory: GHSA-grr9-747v-xvcp
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-grr9-747v-xvcp
Type: github-advisory

## Affected
- NuGet: `scriban` — affected >=0 <6.6.0
- NuGet: `Scriban.Signed` — affected >=0 <6.6.0

## Details
When Scriban renders an object that contains a circular reference, it traverses the object's members infinitely. Because the `ObjectRecursionLimit` property defaults to unlimited, this behavior exhausts the thread's stack space, triggering an uncatchable `StackOverflowException` that immediately terminates the hosting process.

When rendering objects (e.g., `{{ obj }}`), the Scriban rendering engine recursively inspects and formats the object's properties. To prevent infinite loops caused by deeply nested or circular data structures, `TemplateContext` contains an `ObjectRecursionLimit` property. 

However, this property currently defaults to `0` (unlimited). If the data context pushed into the template contains a circular reference, the renderer will recurse indefinitely. This is especially dangerous for web applications that map user-controlled payloads (like JSON) directly to rendering contexts, or for applications that pass ORM objects (like Entity Framework models, which frequently contain circular navigation properties) into the template.

#### Proof of Concept (PoC)
The following C# code demonstrates the vulnerability. Executing this will cause an immediate, fatal `StackOverflowException`, bypassing any standard error handling.

```csharp
using Scriban;
using Scriban.Runtime;

var template = Template.Parse("{{ a }}");
var context = new TemplateContext();
var a = new ScriptObject();

// Introduce a cycle
a["self"] = a;
context.PushGlobal(new ScriptObject { { "a", a } });

try {
  // This crashes the entire process immediately
  template.Render(context);
} catch (Exception ex) {
  // This will never execute because StackOverflowException
  Console.WriteLine("Caught exception: " + ex.Message);
}
```

#### Impact
This vulnerability allows a Denial of Service (DoS) attack. If a malicious user can manipulate the data structure passed to the renderer to include a cyclic reference, or if the application passes a complex object graph to an untrusted template, the entire .NET hosting process will crash.

#### Suggested Remediation
Update `TemplateContext.cs` to set `ObjectRecursionLimit` to a safe default, such as `20`.

```csharp
public int ObjectRecursionLimit { get; set; } = 20;
```
By implementing this default, circular references will gracefully result in a catchable `ScriptRuntimeException` rather than a fatal process crash.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-grr9-747v-xvcp
- https://github.com/scriban/scriban/commit/a6fe6074199e5c04f4d29dc8d8e652b24d33e3e4
- https://github.com/scriban/scriban
