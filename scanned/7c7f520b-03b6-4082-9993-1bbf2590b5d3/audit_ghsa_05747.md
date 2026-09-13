# [C] AdonisJS Path Traversal in Multipart File Handling

## Summary
Severity: Critical
Advisory: GHSA-gvq6-hvvp-h34h
CVE: CVE-2026-21440
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-gvq6-hvvp-h34h
Type: github-advisory

## Affected
- npm: `@adonisjs/bodyparser` — affected >=0 <10.1.2
- npm: `@adonisjs/bodyparser` — affected >=11.0.0-next.0 <11.0.0-next.6

## Details
### Summary

**Description**
A Path Traversal (CWE-22) vulnerability in AdonisJS multipart file handling may allow a remote attacker to write arbitrary files to arbitrary locations on the server filesystem. This impacts @adonisjs/bodyparser through version 10.1.1 and 11.x prerelease versions prior to 11.0.0-next.6. This issue has been patched in @adonisjs/bodyparser versions 10.1.2 and 11.0.0-next.6.

### Details
AdonisJS parses `multipart/form-data` via `BodyParser` and exposes uploads as `MultipartFile`. The issue is in the `MultipartFile.move(location, options)` default options. If `options.name` isn't provided, it defaults to the unsanitized client filename and builds the destination with `path.join(location, name)`, allowing a traversal to escape the default or intended directory chosen by the developer. If `options.overwrite` isn't provided, it defaults to true, allowing file overwrites. The documentation previously demonstrated examples leading developers to this vulnerable code path.
### Impact

Exploitation requires a reachable upload endpoint. If a developer uses `MultipartFile.move()` without the second `options` argument or without explicitly sanitizing the filename, an attacker can supply a crafted `filename` value containing traversal sequences, writing to a destination path outside the intended upload directory. This can lead to arbitrary file write on the server.

If the attacker can overwrite application code, startup scripts, or configuration files that are later executed/loaded, RCE is possible. RCE is not guaranteed and depends on filesystem permissions, deployment layout, and application/runtime behavior.

### Patches
Fixes targeting v6 and v7 have been published below.
- https://github.com/adonisjs/bodyparser/releases/tag/v10.1.2
- https://github.com/adonisjs/bodyparser/releases/tag/v11.0.0-next.6

## References
- https://github.com/adonisjs/core/security/advisories/GHSA-gvq6-hvvp-h34h
- https://nvd.nist.gov/vuln/detail/CVE-2026-21440
- https://github.com/adonisjs/bodyparser/commit/143a16f35602be8561215611582211dec280cae6
- https://github.com/adonisjs/bodyparser/commit/6795c0e3fa824ae275bbd992aae60609e96f0f03
- https://github.com/adonisjs/bodyparser/releases/tag/v10.1.2
- https://github.com/adonisjs/bodyparser/releases/tag/v11.0.0-next.6
- https://github.com/adonisjs/core
