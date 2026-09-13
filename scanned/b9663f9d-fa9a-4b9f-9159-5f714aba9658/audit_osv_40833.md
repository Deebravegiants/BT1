# [H] pnpm: stage download writes outside destination via manifest version traversal

## Summary
Severity: High
Advisory: CVE-2026-55700
Aliases: GHSA-v23m-ccfg-pq9h
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55700
Type: osv

## Details
pnpm is a package manager. From 11.3.0 until 11.5.3, `pnpm stage download` derived a local filename from registry-controlled package name and version fields. A crafted manifest could escape the selected download directory and overwrite another reachable file. The merged fix validates both fields, derives one safe filename, and verifies the final destination before writing. This vulnerability is fixed in 11.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55700.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-v23m-ccfg-pq9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55700
- https://github.com/pnpm/pnpm/pull/12303
