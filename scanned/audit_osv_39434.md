# [M] ThorVG: Null pointer dereference in SVG loader causes crash via 6-byte malformed input

## Summary
Severity: Medium
Advisory: CVE-2026-45729
Aliases: GHSA-f863-8ghq-7h64
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45729
Type: osv

## Details
Thor Vector Graphics (ThorVG) is a production-ready vector graphics engine. Prior to version 1.0.5, a null pointer dereference in SvgLoader::run() allows any caller that passes untrusted SVG data to Picture::load() to crash the process with a 6-byte payload. This issue has been patched in version 1.0.5.

## References
- https://github.com/thorvg/thorvg/releases/tag/v1.0.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45729.json
- https://github.com/thorvg/thorvg/security/advisories/GHSA-f863-8ghq-7h64
- https://nvd.nist.gov/vuln/detail/CVE-2026-45729
- https://github.com/thorvg/thorvg/commit/159f44fd5e3d2eea1b3a70689a894e657e2bb079
- https://github.com/thorvg/thorvg/pull/4387
