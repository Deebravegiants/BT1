# [H] DotVVM allows path traversal when deployed in Debug mode

## Summary
Severity: High
Advisory: GHSA-6q65-j4jw-9cg8
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-19
Source: https://github.com/advisories/GHSA-6q65-j4jw-9cg8
Type: github-advisory

## Affected
- NuGet: `DotVVM` — affected >=4.3.0-preview01-final <4.3.8
- NuGet: `DotVVM` — affected >=5.0.0-preview01-final <5.0.0-preview03-final
- NuGet: `DotVVM` — affected >=0 <4.2.10

## Details
### Description

There is a path traversal vulnerability in any DotVVM application started in Debug mode, if at least one resource with the `FileResourceLocation` has been added. The vulnerability allows an attacker to read arbitrary files from the filesystem accessible by the web application (i.e. appsettings.json or other files containing secrets).

### Patches

The bug is patched in versions  **4.2.10**, **4.3.8** and **5.0.0-preview03-final** (and newer).

Apart from updating DotVVM, it is also recommend invalidating any secrets which could have been leaked by an application deployed in Debug mode (such as database passwords).

### Workarounds

If you cannot update to a patched version, avoid running a publicly accessible DotVVM application in Debug mode (Development environment in Asp.Net Core). It is recommend adding the following statement to the DotvvmStartup class:

```
    config.Debug = false; // TODO: workaround for GHSA-6q65-j4jw-9cg8, remove after updating DotVVM
```

## References
- https://github.com/riganti/dotvvm/security/advisories/GHSA-6q65-j4jw-9cg8
- https://github.com/riganti/dotvvm/commit/68db0110beeda4e8e4be1b7c4e480ef876895bb5
- https://github.com/riganti/dotvvm
