# [H] Scriban has a Stack Overflow via Nested Array Initializers That Bypass the ExpressionDepthLimit Fix

## Summary
Severity: High
Advisory: GHSA-p6q4-fgr8-vx4p
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-p6q4-fgr8-vx4p
Type: github-advisory

## Affected
- NuGet: `Scriban` — affected >=0 <7.0.0
- NuGet: `Scriban.Signed` — affected >=0 <7.0.0

## Details
### Summary
StackOverflowException via nested array initializers bypasses ExpressionDepthLimit fix (GHSA-wgh7-7m3c-fx25)

### Details
The recent fix for GHSA-wgh7-7m3c-fx25 (uncontrolled recursion in parser) added `ExpressionDepthLimit` defaulting to 250. However, deeply nested **array initializers** (`[[[[...`) recurse through `ParseArrayInitializer` → `ParseExpression` → `ParseArrayInitializer`, which is a **different recursion path** not covered by the expression depth counter.

This causes a `StackOverflowException` on current main (commit b5ac4bf - "Add limits for default safety").

### PoC
```
using Scriban;

// ExpressionDepthLimit (default 250) does NOT prevent this crash
string nested = "{{ " + new string('[', 5000) + "1" + new string(']', 5000) + " }}";
Template.Parse(nested); // StackOverflowException - process terminates
```

### Impact
Same as GHSA-wgh7-7m3c-fx25: High severity. StackOverflowException cannot be caught with try/catch in .NET - the process terminates immediately. Any application calling Template.Parse with untrusted input is vulnerable, even with the new default ExpressionDepthLimit enabled.

## References
- https://github.com/scriban/scriban/security/advisories/GHSA-p6q4-fgr8-vx4p
- https://github.com/advisories/GHSA-wgh7-7m3c-fx25
- https://github.com/scriban/scriban
