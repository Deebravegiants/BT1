# [C] Remote Code Execution (RCE) via String Literal Injection into math-codegen

## Summary
Severity: Critical
Advisory: GHSA-p6x5-p4xf-cc4r
CVE: CVE-2026-41507
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-p6x5-p4xf-cc4r
Type: github-advisory

## Affected
- npm: `math-codegen` — affected >=0 <0.4.3

## Details
### Impact

String literal content passed to `cg.parse()` is injected verbatim into a `new Function()` body without sanitization. This allows an attacker to execute arbitrary system commands when user-controlled input reaches the parser. Any application exposing a math evaluation endpoint where user input flows into `cg.parse()` is vulnerable to full RCE.
    
### Patches

The vulnerability is addressed by using `JSON.stringify()` on string literal values in `lib/node/ConstantNode.js` to ensure they are treated as data rather than code. Users should upgrade to version 0.4.3 or later.
    
### Workarounds

Avoid passing un-sanitized user input to the parser or manually escape string literals in the input.

## References
- https://github.com/mauriciopoppe/math-codegen/security/advisories/GHSA-p6x5-p4xf-cc4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41507
- https://github.com/mauriciopoppe/math-codegen/pull/11
- https://github.com/mauriciopoppe/math-codegen/commit/4bb52d3030683362b3559ee8dd91350555a05f6b
- https://github.com/hits3134
- https://github.com/mauriciopoppe/math-codegen
