# [M] OpenClaw's skills-install-download can be redirected outside the tools root by rebinding the validated base path

## Summary
Severity: Medium
Advisory: GHSA-vhwf-4x96-vqx2
CVE: CVE-2026-33574
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-vhwf-4x96-vqx2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.8

## Details
OpenClaw's skills download installer validated the intended per-skill tools root lexically, but later reused that mutable path while downloading and copying the archive into place. If a local attacker could rebind that tools-root path between validation and the final write, the installer could be redirected to write outside the intended tools directory.

The fix pins the canonical per-skill tools root immediately after validation and derives later download/copy paths from that canonical root, so rebinding the lexical path fails closed instead of redirecting the write.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.3.7`
- Affected range: `<= 2026.3.7`
- Fixed in released version: `2026.3.8`

## Fix Commit(s)

- `9abf014f3502009faf9c73df5ca2cff719e54639`

## Release Verification

- Verified fixed in GitHub release `v2026.3.8` published on March 9, 2026.
- Verified `npm view openclaw version` resolves to `2026.3.8`.
- Verified the release contains the regression test covering tools-root rebinding and that the test passes against the `v2026.3.8` tree.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vhwf-4x96-vqx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33574
- https://github.com/openclaw/openclaw/commit/9abf014f3502009faf9c73df5ca2cff719e54639
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-via-tools-root-rebinding-in-skills-download
