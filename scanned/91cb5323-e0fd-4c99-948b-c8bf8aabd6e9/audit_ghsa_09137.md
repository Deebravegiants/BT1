# [C] Electerm Local code through electerm's single-instance socket

## Summary
Severity: Critical
Advisory: GHSA-7p5m-v798-f8vv
CVE: CVE-2026-45353
CWE: CWE-732, CWE-94, CWE-940
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-7p5m-v798-f8vv
Type: github-advisory

## Affected
- npm: `electerm` — affected >=3.0.6 <3.9.0

## Details
### Impact
_Local code execution without UI interaction: any same-user process can send a JSON payload to electerm's single-instance socket/pipe, causing the app to create tabs and potentially spawn attacker-controlled local processes. Affects electerm single-instance installs on the machine._

### Patches

- https://github.com/electerm/electerm/commit/0599e67069b00e376a2e962649aaad6096e63507

### Workarounds

- Do not run unsafe command 

### References
- Report / credit: https://github.com/Curly-Haired-Baboon
- Electerm releases: https://github.com/electerm/electerm/releases

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-7p5m-v798-f8vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45353
- https://github.com/electerm/electerm/commit/0599e67069b00e376a2e962649aaad6096e63507
- https://github.com/electerm/electerm
