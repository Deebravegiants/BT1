# [H] Microsoft Kiota: Code Generation Literal Injection in Kiota Ruby Generator

## Summary
Severity: High
Advisory: GHSA-xg2h-5xr2-29jw
CVE: CVE-2026-59861
CWE: CWE-94
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-xg2h-5xr2-29jw
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenAPI.Kiota` — affected >=1.30.0 <1.32.0
- NuGet: `Microsoft.OpenAPI.Kiota.Builder` — affected >=1.30.0 <1.32.0
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=0 <1.29.1
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=0 <1.29.1

## Details
Code Generation Literal Injection in Kiota Ruby Generator Leads to Arbitrary Code Execution

# Impact

The Kiota Ruby code generator is vulnerable to a code generation literal injection attack. The generator embeds string values from OpenAPI default fields and property names directly into Ruby double-quoted string literals without properly escaping the # character. Since Ruby evaluates string interpolation expressions like #{expr}, #$var, and #@var within double-quoted strings at runtime, an attacker who controls an OpenAPI specification file can inject arbitrary Ruby code into generated model classes.

# Who is impacted

Developers using Kiota to generate Ruby API clients from external or untrusted OpenAPI specifications
Teams with CI/CD pipelines configured to automatically regenerate client code from remote specs
Applications that deploy generated Ruby code to production servers

# Vulnerability details

Affected component: CodeMethodWriter.cs
Root cause: The shared SanitizeForQuotedLiteral() function in Writers/StringExtensions.cs does not escape the # character

# Attack vectors

OpenAPI default fields in schema properties
Property wire-name hash keys in deserializer/serializer methods
Any schema-derived string embedded in Ruby double-quoted literals
Severity: Critical when generated code reaches production; High for CI/CD environments with access to production secrets; Medium for public third-party specs; Low for developer-controlled specs.

# Patches

https://github.com/microsoft/kiota/pull/7746

# Workarounds

If you cannot upgrade immediately:

1. Audit and sanitize OpenAPI specifications: Review all OpenAPI specification files for any default values or property names containing the # character. Remove or replace any suspicious strings before code generation.
1. Code review of generated files: Implement mandatory code review of all generated Ruby files before merging into any branch. Look for double-quoted strings containing #{, #$, or #@ patterns.
1. Restrict specification sources: Only consume OpenAPI specifications from trusted internal sources. Avoid automatic code generation from external or third-party APIs until this patch is applied.
1. Isolate generated code from production: Do not deploy generated Ruby models to production environments unless the specification source has been verified and reviewed.
1. Manual escaping (temporary): If regeneration is not possible, manually inspect and edit generated files to escape any # characters in string literals (replace # with \# in double-quoted strings).

# Remediation

Upgrade Kiota to 1.29.1, 1.32.0, or later.
Regenerate/refresh existing generated clients as a precaution:

```shell
kiota update
```

Refreshing generated clients ensures previously generated vulnerable code is replaced with hardened output.

## References
- https://github.com/microsoft/kiota/security/advisories/GHSA-xg2h-5xr2-29jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-59861
- https://github.com/microsoft/kiota/pull/7746
- https://github.com/microsoft/kiota/commit/fee1b648bb4394ba7ba72de9c0ce4f2a0bad0cb6
- https://github.com/microsoft/kiota
- https://github.com/microsoft/kiota/releases/tag/v1.32.0
