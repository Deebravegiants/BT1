# [H] Microsoft Kiota: XML Doc-Comment Newline Breakout Code Injection

## Summary
Severity: High
Advisory: GHSA-3hrf-2gc2-mx32
CVE: CVE-2026-59860
CWE: CWE-94
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-3hrf-2gc2-mx32
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=1.30.0 <1.32.3
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=1.30.0 <1.32.3
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=0 <1.29.1
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=0 <1.29.1

## Details
### Summary

Kiota versions **prior to 1.32.3 and 1.29.1** are affected by a code-generation injection vulnerability in the C# XML documentation-comment sink (the `description`, `externalDocs` label, and `externalDocs` link fields emitted as `/// …` comments).

When text from an OpenAPI description is written into single-line XML doc comments without stripping newline and Unicode line-terminator characters, an attacker can break out of the `///` comment line and inject additional code into generated C# clients.

## Impact and Preconditions

This issue is only practically exploitable when:

1.  the OpenAPI description used for generation is from an **untrusted source**, or
2.  a normally trusted OpenAPI description has been **compromised/tampered with**.

The injected code is compiled (and may execute) when the developer or CI **builds** the generated client. If you only generate from trusted, integrity-protected API descriptions, risk is significantly reduced.

## Affected Versions

- **Affected:** all versions **< 1.29.1**, **>= 1.30.0, < 1.32.3**
- **Fixed: 1.29.1, 1.32.3,** and later

## Illustrative Exploit Example

### Example OpenAPI fragment (malicious description)

```yaml
openapi: 3.0.1
info:
  title: Exploit Demo
  version: 1.0.0
  description: |-
    Legitimate summary text
    public static class Pwned { static Pwned() { System.Diagnostics.Process.Start("calc.exe"); } }
```

The newline inside `description` (also exploitable via `\r`, U+0085, U+2028, U+2029) terminates the doc-comment line.

### Example generated C# snippet before fix (illustrative)

```csharp
/// Legitimate summary text
public static class Pwned { static Pwned() { System.Diagnostics.Process.Start("calc.exe"); } }
```

The injected payload escapes the intended `///` comment context and introduces attacker-controlled statements in generated code.

> Note: this exploit is not limited to the `description` field, but may also impact the `externalDocs` label and link text and other doc-comment-derived locations.

## Remediation

1.  Upgrade Kiota to **1.32.3 or later**.
2.  Regenerate/refresh existing generated clients as a precaution:

Refreshing generated clients ensures previously generated vulnerable code is replaced with hardened output. The fix (PR microsoft/kiota#7831) strips `\r`, `\n`, `\u0085`, `\u2028`, `\u2029` (and normalizes tabs) from description, label, and link text before emitting doc comments.

## References
- https://github.com/microsoft/kiota/security/advisories/GHSA-3hrf-2gc2-mx32
- https://nvd.nist.gov/vuln/detail/CVE-2026-59860
- https://github.com/microsoft/kiota/pull/7831
- https://github.com/microsoft/kiota/commit/ebb632db90aa8e3c20949337d9faa2720d64ca44
- https://github.com/microsoft/kiota
- https://github.com/microsoft/kiota/releases/tag/v1.32.3
