# [H] OpenClaw has a command injection in maintainer clawtributors updater

## Summary
Severity: High
Advisory: GHSA-m7x8-2w3w-pr42
CVE: CVE-2026-26323
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-m7x8-2w3w-pr42
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.8 <2026.2.14

## Details
### Summary
Command injection in the maintainer/dev script `scripts/update-clawtributors.ts`.

### Impact
Affects contributors/maintainers (or CI) who run `bun scripts/update-clawtributors.ts` in a source checkout that contains a malicious commit author email (e.g. crafted `@users.noreply.github.com` values).

Normal CLI usage is not affected (`npm i -g openclaw`): this script is not part of the shipped CLI and is not executed during routine operation.

### Affected Versions
- Source checkouts: tags `v2026.1.8` through `v2026.2.13` (inclusive)
- Version range (structured): `>= 2026.1.8, < 2026.2.14`

### Details
The script derived a GitHub login from `git log` author metadata and interpolated it into a shell command (via `execSync`). A malicious commit record could inject shell metacharacters and execute arbitrary commands when the script is run.

### Fix
- Fix commit: `a429380e337152746031d290432a4b93aa553d55`
- Planned patched version: `2026.2.14`

### Credits
Thanks @scanleale and @MegaManSec (https://joshua.hu) of [AISLE Research Team](https://aisle.com/) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m7x8-2w3w-pr42
- https://nvd.nist.gov/vuln/detail/CVE-2026-26323
- https://github.com/openclaw/openclaw/commit/a429380e337152746031d290432a4b93aa553d55
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
