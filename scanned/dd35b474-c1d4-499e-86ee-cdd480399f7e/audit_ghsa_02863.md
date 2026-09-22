# [M] Electron's sandboxed renderers can obtain thumbnails of arbitrary files through the nativeImage API

## Summary
Severity: Medium
Advisory: GHSA-mpjm-v997-c4h4
CVE: CVE-2021-39184
CWE: CWE-668, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-mpjm-v997-c4h4
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <11.5.0
- npm: `electron` — affected >=12.0.0 <12.1.0
- npm: `electron` — affected >=13.0.0 <13.3.0

## Details
### Impact
This vulnerability allows a sandboxed renderer to request a "thumbnail" image of an arbitrary file on the user's system. The thumbnail can potentially include significant parts of the original file, including textual data in many cases.

All current stable versions of Electron are affected.

### Patches
This was fixed with #30728, and the following Electron versions contain the fix:

- 15.0.0-alpha.10
- 14.0.0
- 13.3.0
- 12.1.0
- 11.5.0

### Workarounds
If your app enables `contextIsolation`, this vulnerability is significantly more difficult for an attacker to exploit.

Further, if your app does not depend on the `createThumbnailFromPath` API, then you can simply disable the functionality. In the main process, before the 'ready' event:
```js
delete require('electron').nativeImage.createThumbnailFromPath
```

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org).

## References
- https://github.com/electron/electron/security/advisories/GHSA-mpjm-v997-c4h4
- https://nvd.nist.gov/vuln/detail/CVE-2021-39184
- https://github.com/electron/electron/pull/30728
- https://github.com/electron/electron/pull/30728/commits/8fed645bd671f359ee52d806c075ec4e07eda17f
- https://github.com/electron/electron
