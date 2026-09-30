# [H] OpenClaw: ZIP extraction race could write outside destination via parent symlink rebind

## Summary
Severity: High
Advisory: GHSA-r54r-wmmq-mh84
CVE: CVE-2026-28483
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-r54r-wmmq-mh84
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
ZIP extraction in OpenClaw could be raced into writing outside the intended destination directory via parent-directory symlink rebind between validation and write.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.3.1`
- Latest published vulnerable version confirmed: `2026.3.1` (npm as of 2026-03-02)
- Patched version: `2026.3.2` (released)

### Technical Details
In `src/infra/archive.ts`, ZIP extraction previously validated output paths, then later opened/truncated the destination path in a separate step. A local race on parent-directory symlink state could redirect the final write outside the extraction root.

The fix hardens ZIP writes by binding writes to the opened file handle identity and avoiding the pre-write truncate race path, with shared fd realpath verification in `src/infra/fs-safe.ts` and regression coverage in `src/infra/archive.test.ts`.

### Fix Commit(s)
- `7dac9b05dd9d38dd3929637f26fa356fd8bdd107`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r54r-wmmq-mh84
- https://github.com/openclaw/openclaw/commit/7dac9b05dd9d38dd3929637f26fa356fd8bdd107
- https://github.com/openclaw/openclaw
