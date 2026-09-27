# [M] Electron: Registry key path injection in app.setAsDefaultProtocolClient on Windows

## Summary
Severity: Medium
Advisory: GHSA-mwmh-mq4g-g6gr
CVE: CVE-2026-34773
CWE: CWE-20, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-mwmh-mq4g-g6gr
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0

## Details
### Impact
On Windows, `app.setAsDefaultProtocolClient(protocol)` did not validate the protocol name before writing to the registry. Apps that pass untrusted input as the protocol name may allow an attacker to write to arbitrary subkeys under `HKCU\Software\Classes\`, potentially hijacking existing protocol handlers.

Apps are only affected if they call `app.setAsDefaultProtocolClient()` with a protocol name derived from external or untrusted input. Apps that use a hardcoded protocol name are not affected.

### Workarounds
Validate the protocol name matches `/^[a-zA-Z][a-zA-Z0-9+.-]*$/` before passing it to `app.setAsDefaultProtocolClient()`.

### Fixed Versions
* `41.0.0`
* `40.8.1`
* `39.8.1`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-mwmh-mq4g-g6gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34773
- https://github.com/electron/electron
