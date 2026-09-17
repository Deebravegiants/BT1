# [M] Electron: nodeIntegrationInWorker not correctly scoped in shared renderer processes

## Summary
Severity: Medium
Advisory: GHSA-xwr5-m59h-vwqr
CVE: CVE-2026-34775
CWE: CWE-653
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-xwr5-m59h-vwqr
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.4
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.4
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0

## Details
### Impact
The `nodeIntegrationInWorker` webPreference was not correctly scoped in all configurations. In certain process-sharing scenarios, workers spawned in frames configured with `nodeIntegrationInWorker: false` could still receive Node.js integration.

Apps are only affected if they enable `nodeIntegrationInWorker`. Apps that do not use `nodeIntegrationInWorker` are not affected.

### Workarounds
Avoid enabling `nodeIntegrationInWorker` in apps that also open child windows or embed content with differing webPreferences.

### Fixed Versions
* `41.0.0`
* `40.8.4`
* `39.8.4`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-xwr5-m59h-vwqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34775
- https://github.com/electron/electron
