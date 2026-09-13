# [C] Microsoft Kiota: Path/URL injection into generated Copilot plugin manifest via x-ai-* extensions

## Summary
Severity: Critical
Advisory: GHSA-4jwf-m4wg-8p66
CVE: CVE-2026-59864
CWE: CWE-22, CWE-829
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-4jwf-m4wg-8p66
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=0 <1.29.1
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=0 <1.29.1

## Details
### Summary

`kiota plugin add` / `kiota plugin generate` (with `-t APIPlugin`) emits an attacker-controlled `static_template.file` path from the AI-plugin extensions (`x-ai-adaptive-card`, `x-ai-capabilities`) **verbatim**, with no path validation, into the generated Microsoft 365 Copilot / Teams plugin manifest (`<name>-apiplugin.json`). An attacker-controlled or compromised OpenAPI description can therefore embed a `../` / absolute path into the manifest's `response_semantics.static_template.file`, yielding a **path traversal (CWE-22)** / out-of-package file inclusion (CWE-829) that is resolved by the AI host when the generated plugin is deployed.

Confirmed on Kiota **1.32.4** (`KIOTA_CONFIG_PREVIEW=true`, the self-contained `linux-x64` release binary).

### Details

Both extension paths write the `static_template.file` reference straight into the manifest without sanitization — `PluginsGenerationService.GetResponseSemanticsFromAdaptiveCardExtension` mints `static_template = {"file": <File>}`, and the `x-ai-capabilities` path copies the `static_template` object through:

```
# spec                                                  -> generated manifest (functions[].capabilities.response_semantics)
x-ai-adaptive-card: {title: T, data_path: $.x,
   file: "../../../../../../etc/passwd"}                -> static_template.file = "../../../../../../etc/passwd"   (CWE-22)
x-ai-capabilities.response_semantics.static_template:
   {file: "../../../../../../etc/passwd"}               -> static_template.file = "../../../../../../etc/passwd"   (CWE-22)
```

(`x-ai-adaptive-card.file` only reaches the manifest when `title` is set, so `GetResponseSemanticsFromAdaptiveCardExtension` fires; otherwise kiota writes its own template card instead.)

### Impact

**This is not local code execution on the build host.** The injected path is written into the generated plugin manifest and realized **downstream**, when the plugin is packaged and sideloaded / deployed to an AI host (Microsoft 365 Copilot / Teams) that resolves `static_template.file` relative to the plugin package (out-of-package file reference via `../`). Kiota is the propagation point: it fails to reject `../` and absolute paths in this provider-supplied field before writing it into the manifest.

### Patches

Fixed in **1.29.1 and 1.32.5** (https://github.com/microsoft/kiota/pull/7892). `static_template.file` from both `x-ai-adaptive-card` and `x-ai-capabilities` is validated as a relative path confined to the plugin output package: absolute URIs, rooted/UNC paths, Windows drive paths, and `..` traversal segments are rejected, and unsafe references are dropped with a warning. Regression tests cover `..`, absolute paths, and URI values.

### Remediation

Upgrade to Kiota **1.29.1, 1.32.5** or later and regenerate affected plugins.

## References
- https://github.com/microsoft/kiota/security/advisories/GHSA-4jwf-m4wg-8p66
- https://nvd.nist.gov/vuln/detail/CVE-2026-59864
- https://github.com/microsoft/kiota/pull/7892
- https://github.com/microsoft/kiota/commit/9a185994a4e549b7bba3cc2beffb9736aa902e79
- https://github.com/microsoft/kiota
- https://github.com/microsoft/kiota/releases/tag/v1.32.5
