# [H] Microsoft.OpenAPI: Circular schema references may terminate OpenAPI parsing

## Summary
Severity: High
Advisory: GHSA-v5pm-xwqc-g5wc
CVE: CVE-2026-49451
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-v5pm-xwqc-g5wc
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenApi` — affected >=2.0.0-preview.11 <2.7.5
- NuGet: `Microsoft.OpenApi` — affected >=3.0.0 <3.5.4

## Details
### Impact

A small OpenAPI document containing a circular schema reference can cause process termination through stack overflow in Microsoft.OpenApi. The issue affects OpenAPI document parsing through public OpenAPI.NET reader APIs and has been confirmed across both JSON and YAML reader paths.

## Affected versions

- `>= 2.0.0-preview.11, <= 2.7.4`
- `>= 3.0.0, <= 3.5.3`

### Patches

- For the 2.X major version, versions 2.7.5 and above are patched.
- For the 3.X major version, versions 3.5.4 and above are patched.
- For the 1.X major version, the issue does not apply since that version of the library *could not* resolve references that pointed to another reference.

## Impact

Applications, CLIs, developer tools, or services that parse untrusted OpenAPI documents in-process may be terminated by a crafted OpenAPI document containing circular schema references.

The impact is availability/process termination only. This report does not claim remote code execution, authentication bypass, credential exposure, privilege escalation, data exposure, or Microsoft hosted service impact.

## Details

A standalone isolated-process harness confirmed repeatable process termination through public OpenAPI.NET reader APIs. The issue reproduces in the affected released NuGet packages and affects both JSON and YAML reader paths.

A separate Microsoft-owned local consumer, `microsoft/kiota`, also reproduces the termination through the `kiota show --openapi <file>` workflow. That workflow parses OpenAPI files in-process using Microsoft.OpenApi and Microsoft.OpenApi.YamlReader.

### Example payload

```json
{
    "openapi": "3.0.0",
    "info": {
        "title": "Test",
        "version": "0.0.1"
    },
    "paths": {},
    "components": {
        "schemas": {
            "A": {
                "$ref": "#/components/schemas/B"
            },
            "B": {
                "$ref": "#/components/schemas/A"
            }
        }
    }
}
```

## Remediation

Users should upgrade to Microsoft.OpenApi `2.7.5` or `3.5.4`, depending on the major version line they consume.

Applications that parse OpenAPI documents from untrusted sources should avoid parsing those documents in the primary application process when possible. Running parsing in an isolated process can reduce the blast radius of parser failures.

## References
- https://github.com/microsoft/OpenAPI.NET/security/advisories/GHSA-v5pm-xwqc-g5wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-49451
- https://github.com/microsoft/OpenAPI.NET
