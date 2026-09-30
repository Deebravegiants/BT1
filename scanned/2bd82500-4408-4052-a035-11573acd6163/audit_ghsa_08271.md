# [C] Electerm users can run dangrous code through link or command line

## Summary
Severity: Critical
Advisory: GHSA-mpm8-cx2p-626q
CVE: CVE-2026-43944
CWE: CWE-20, CWE-829, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-mpm8-cx2p-626q
Type: github-advisory

## Affected
- npm: `electerm` — affected >=3.0.6 <3.8.8

## Details
### Impact
_Arbitrary local code execution via deep links, CLI `--opts`, or crafted shortcuts. Affected users: electerm installs that accept protocol URLs or CLI options (affected versions listed in the original report). Exploit requires clicking a crafted `electerm://...` link or opening a crafted shortcut/command that launches electerm with attacker-controlled `opts`._

### Patches
Fixed in version > 3.8.8

commits:

- https://github.com/electerm/electerm/commit/8a6a17951e96d715f5a231532bbd8303fe208700
- https://github.com/electerm/electerm/commit/a79e06f4a1f0ac6376c3d2411ef4690fa0377742
- https://github.com/electerm/electerm/commit/0599e67069b00e376a2e962649aaad6096e63507

### Workarounds
- Disable or unregister electerm protocol handlers (Deep Link settings) and avoid clicking `electerm://` links.
- Do not run electerm with untrusted `--opts` arguments or open `.lnk` / `.desktop` files from untrusted sources.
- Restrict which users can launch electerm on shared machines and avoid leaving electerm installed in locations reachable by other users.
- As a temporary measure, run electerm in a confined account or sandbox (non-admin user) to reduce impact.

### References
- Report / credit: https://github.com/Curly-Haired-Baboon
- Electerm releases: https://github.com/electerm/electerm/releases

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-mpm8-cx2p-626q
- https://nvd.nist.gov/vuln/detail/CVE-2026-43944
- https://github.com/electerm/electerm/commit/0599e67069b00e376a2e962649aaad6096e63507
- https://github.com/electerm/electerm/commit/8a6a17951e96d715f5a231532bbd8303fe208700
- https://github.com/electerm/electerm/commit/a79e06f4a1f0ac6376c3d2411ef4690fa0377742
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/releases/tag/v3.8.15
