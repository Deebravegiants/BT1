# [H] Microsoft Kiota: Arbitrary file write + code-injection via x-ms-kiota-info clientClassName and clientNamespaceName

## Summary
Severity: High
Advisory: GHSA-4vv7-jj25-4gh6
CVE: CVE-2026-59866
CWE: CWE-22, CWE-94
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-4vv7-jj25-4gh6
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=0 <1.29.1
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=0 <1.29.1

## Details
### Summary

Microsoft Kiota emitted the `x-ms-kiota-info` extension's `clientClassName` or `clientNamespaceName` value
**raw**, with no identifier or path sanitization, as **both** the generated client's class/namespace name
**and** part of the generated output path. When `kiota generate` is run **without `-c/--class-name`** — the
zero-config workflow that `x-ms-kiota-info` is explicitly designed for (the API provider supplies the names in
the description so consumers don't have to) — an attacker who controls or tampers with the OpenAPI description
could therefore:

- **(CWE-22) write the generated source file to a path outside the `-o` output directory** — e.g.
  `clientClassName: "/var/www/html/shell"`; and
- **(CWE-94) inject arbitrary text into the generated class/namespace declaration**, corrupting the generated
  client.

Confirmed on Kiota **1.32.4** (the self-contained `linux-x64` release binary), i.e. **after** the earlier
writer-sink hardening — that fix escaped property/enum/default/serialization sinks but never sanitized the
provider-supplied `clientClassName` / `clientNamespaceName`.

### Details

`clientClassName` reached two unsanitized sinks (observed in the generated C#; the same raw emission occurred
for Java, Go, TypeScript, Python, and PHP):

```
# output FILENAME (CWE-22): clientClassName flows into the file path
clientClassName: "/abs/path/PWNED"   ->   /abs/path/PWNED.cs   (written outside -o)

# class declaration (CWE-94): clientClassName flows verbatim into the type declaration
clientClassName: 'Pwn { } public class INJECTED { } public partial class RealClient'
   ->  public partial class Pwn { } public class INJECTED { } public partial class RealClient : ... { }
```

`clientNamespaceName` reached the analogous namespace/path sinks.

### Impact

A developer or CI host generating a client from an attacker-controlled or compromised OpenAPI description
(without `-c`) could create/overwrite a generated source file at an attacker-influenced path and emit
attacker-controlled text into the generated client.

This does **not** reach clean remote code execution: because `clientClassName` is reused verbatim at multiple
sites (the class name **and** the constructor name), injected code cannot be made to compile — it breaks the
build. So the code-injection vector is a generation/build-corruption (integrity/DoS), and the high-severity
primitive is the file write. CWE-22 / CWE-94.

### Patches

Fixed in **1.29.1 and 1.32.5** (https://github.com/microsoft/kiota/pull/7884). `clientClassName` and
`clientNamespaceName` sourced from `x-ms-kiota-info` are now sanitized before use:
`GenerationConfiguration.SanitizeClientClassName` strips any character outside `[A-Za-z0-9_]` and any invalid
leading character (falling back to `ApiClient`), and `SanitizeClientNamespaceName` restricts to
`[A-Za-z0-9._-]`, collapses consecutive dots, strips invalid leading characters (falling back to `ApiSdk`).
This removes path separators, drive/colon, `..`, quotes, and braces, so the values can no longer influence
the output path or inject into the declaration.

### Remediation

Upgrade to Kiota **1.29.1, 1.32.5,** or later and regenerate affected clients.

## References
- https://github.com/microsoft/kiota/security/advisories/GHSA-4vv7-jj25-4gh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-59866
- https://github.com/microsoft/kiota/pull/7884
- https://github.com/microsoft/kiota/commit/dc812dbbf88ef7edf53a890d36b2f9d1460e947d
- https://github.com/microsoft/kiota
- https://github.com/microsoft/kiota/releases/tag/v1.32.5
