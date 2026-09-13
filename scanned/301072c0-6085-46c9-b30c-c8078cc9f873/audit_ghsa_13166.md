# [M] Electron context isolation bypass via nested unserializable return value

## Summary
Severity: Medium
Advisory: GHSA-p7v2-p9m8-qqg7
CVE: CVE-2023-29198
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-p7v2-p9m8-qqg7
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <22.3.6
- npm: `electron` — affected >=23.0.0-alpha.1 <23.2.3
- npm: `electron` — affected >=24.0.0-alpha.1 <24.0.1
- npm: `electron` — affected >=25.0.0-alpha.1 <25.0.0-alpha.2

## Details
### Impact
Apps using `contextIsolation` and `contextBridge` are affected.

This is a context isolation bypass, meaning that code running in the main world context in the renderer can reach into the isolated Electron context and perform privileged actions.

### Workarounds
This issue is exploitable under either of two conditions:
* If an API exposed to the main world via `contextBridge` can return an object or array that contains a JS object which cannot be serialized, for instance, a canvas rendering context. This would normally result in an exception being thrown `Error: object could not be cloned`.
* If an API exposed to the main world via `contextBridge` has a return value that throws a user-generated exception while being sent over the bridge, for instance a dynamic getter property on an object that throws an error when being computed.

The app side workaround is to ensure that such a case is not possible. Ensure all values returned from a function exposed over the context bridge are [supported](https://www.electronjs.org/docs/latest/api/context-bridge#parameter--error--return-type-support) and that any objects returned from functions do not have dynamic getters that can throw exceptions.

Auditing your exposed API is likely to be quite difficult so we strongly recommend you update to a patched version of Electron.

### Fixed Versions
* `25.0.0-alpha.2`
* `24.0.1`
* `23.2.3`
* `22.3.6`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-p7v2-p9m8-qqg7
- https://nvd.nist.gov/vuln/detail/CVE-2023-29198
- https://github.com/electron/electron
- https://www.electronjs.org/docs/latest/api/context-bridge#parameter--error--return-type-support
