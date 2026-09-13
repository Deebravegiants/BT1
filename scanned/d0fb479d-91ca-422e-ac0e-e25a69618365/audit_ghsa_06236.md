# [H] Electron: Sandboxed iframe can bypass the allow-popups restriction via the OpenURL navigation path

## Summary
Severity: High
Advisory: GHSA-9f4c-93c8-jc8g
CVE: CVE-2026-70608
CWE: CWE-1021, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-9f4c-93c8-jc8g
Type: github-advisory

## Affected
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.1
- npm: `electron` — affected >=40.0.0-alpha.1 <41.10.3
- npm: `electron` — affected >=0 <39.8.10

## Details
### Impact
A sandboxed iframe without the `allow-popups` keyword could still open a new window (or trigger `setWindowOpenHandler`) with no user interaction, because new-window navigations taking the OpenURL path did not apply the iframe sandbox popup restriction.

Apps that embed untrusted content in sandboxed iframes and rely on the absence of `allow-popups` to prevent window creation are affected. Apps that deny window creation in `setWindowOpenHandler`, or that do not embed untrusted content in sandboxed iframes, are not affected.

### Workarounds
Return `{ action: 'deny' }` from `setWindowOpenHandler` for any content you do not trust, rather than relying on the iframe sandbox alone.

### Fixed Versions
* `42.0.1`
* `41.10.3`
* `39.8.10`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-9f4c-93c8-jc8g
- https://github.com/electron/electron/pull/51437
- https://github.com/electron/electron/pull/51438
- https://github.com/electron/electron/pull/51439
- https://github.com/electron/electron/commit/3ff23c52ab364a0afc6ab5bd7851291d3159de57
- https://github.com/electron/electron/commit/57cbe329c4ae8aab5ac5ebdcb588adc9a11de0d3
- https://github.com/electron/electron/commit/68cf8b7d9122260f6b534a69a82c701a56cf159f
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.10
- https://github.com/electron/electron/releases/tag/v41.10.3
- https://github.com/electron/electron/releases/tag/v42.0.1
