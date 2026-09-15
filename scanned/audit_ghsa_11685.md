# [H] Scriban has Uncontrolled Recursion in Parser Leads to Stack Overflow and Process Crash (Denial of Service)

## Summary
Severity: High
Advisory: GHSA-wgh7-7m3c-fx25
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-wgh7-7m3c-fx25
Type: github-advisory

## Affected
- NuGet: `scriban` — affected >=0 <6.6.0
- NuGet: `Scriban.Signed` — affected >=0 <6.6.0

## Details
Scriban is vulnerable to an uncontrolled process crash resulting in a Denial of Service. Because the recursive-descent parser does not enforce a default limit on expression depth, an attacker who controls template input can craft a heavily nested template that triggers a `StackOverflowException`. In .NET, a `StackOverflowException` cannot be caught by standard `try-catch` blocks, resulting in the immediate and ungraceful termination of the entire hosting process. 

Scriban utilizes a recursive-descent parser to process template expressions. While the library exposes an `ExpressionDepthLimit` property in its `ParserOptions`, this property defaults to `null` (disabled). 

If an application accepts user-supplied templates (or dynamically constructs templates from untrusted input), an attacker can supply thousands of nested parentheses or blocks. As the parser recursively evaluates each nested layer, it consumes thread stack space until it exceeds the limits of the host OS, triggering a fatal crash.

#### Impact

An attacker can supply crafted input that triggers a `StackOverflowException`, causing immediate termination of the hosting process and resulting in a Denial of Service. In applications that process untrusted or user-controlled templates (e.g., web applications or APIs), this can be exploited remotely without authentication. The failure is not recoverable, requiring a full process restart and leading to service disruption.

#### Proof of Concept (PoC)
The following C# code demonstrates the vulnerability. Executing this code will immediately terminate the application process.

```csharp
using Scriban;

// Creates a deeply nested expression: (((( ... (1) ... ))))
string nested = new string('(', 10000) + "1" + new string(')', 10000);

try {
  // This will crash the entire process immediately
  Scriban.Template.Parse("{{ " + nested + " }}");
} catch (Exception ex) {
  // This catch block will never execute because StackOverflowException
  Console.WriteLine("Caught exception: " + ex.Message);
}
```

#### Suggested Remediation

Update the `ParserOptions` constructor (or the internal parser initialization) to set a default value for `ExpressionDepthLimit`. A limit of `1000` (or even lower, such as `250` or `500`) is generally more than enough for legitimate templates while safely preventing stack exhaustion.

```csharp
public int? ExpressionDepthLimit { get; set; } = 250; 
```
Alternatively, document the risk heavily and warn developers to manually set `ExpressionDepthLimit` if evaluating untrusted templates, though a secure-by-default approach is strongly preferred.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-wgh7-7m3c-fx25
- https://github.com/scriban/scriban/commit/a6fe6074199e5c04f4d29dc8d8e652b24d33e3e4
- https://github.com/scriban/scriban/commit/b5ac4bf30459fdc76964e3f751e16f7e96079ea7
- https://github.com/scriban/scriban
