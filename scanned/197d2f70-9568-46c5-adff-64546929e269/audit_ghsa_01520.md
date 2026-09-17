# [M] Arbitrary file read via window-open IPC in Electron

## Summary
Severity: Medium
Advisory: GHSA-f9mq-jph6-9mhm
CVE: CVE-2020-4075
CWE: CWE-552
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-f9mq-jph6-9mhm
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <7.2.4
- npm: `electron` — affected >=8.0.0 <8.2.4

## Details
### Impact
The vulnerability allows arbitrary local file read by defining unsafe window options on a child window opened via window.open.

### Workarounds
Ensure you are calling `event.preventDefault()` on all [`new-window`](https://electronjs.org/docs/api/web-contents#event-new-window) events where the `url` or `options` is not something you expect.

### Fixed Versions
* `9.0.0-beta.21`
* `8.2.4`
* `7.2.4`

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-f9mq-jph6-9mhm
- https://nvd.nist.gov/vuln/detail/CVE-2020-4075
- https://www.electronjs.org/releases/stable?page=3#release-notes-for-v824
