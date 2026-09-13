# [M] JLSEC-2026-1379

## Summary
Severity: Medium
Advisory: JLSEC-2026-1379
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1379
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected unspecified

## Details
Mongoose is an embedded web server and network library. Prior to 7.22, an attacker who can control an SSI-enabled file can place directory traversal sequences in an #include file or #include virtual directive. The `mg_ssi()` function in `src/ssi.c` concatenates the directive argument into a filesystem path without calling `mg_path_is_sane()`, allowing an `MG_ENABLE_SSI` deployment with `ssi_pattern` configured to disclose files readable by the Mongoose process. This issue is fixed in version 7.22.

## References
- https://github.com/cesanta/mongoose/commit/a9df523f76f43a38bd53b4232b9cfd4c16869e71
- https://github.com/cesanta/mongoose/pull/3611
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/cesanta/mongoose/security/advisories/GHSA-h7m9-764r-7x4x
