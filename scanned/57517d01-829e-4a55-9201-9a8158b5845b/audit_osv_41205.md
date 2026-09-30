# [H] Appium: Unauthenticated arbitrary file/directory deletion in @appium/storage-plugin

## Summary
Severity: High
Advisory: CVE-2026-58192
Aliases: GHSA-jwgx-mp9m-jwcr
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-58192
Type: osv

## Details
Appium is a cross-platform automation framework for all kinds of apps, built on top of the W3C WebDriver protocol. Prior to 1.1.6, the Appium storage plugin exposes POST /storage/delete, whose handler passes the user-supplied name value directly into path.join(storageRoot, name) and fs.rimraf() without path sanitization, allowing an unauthenticated remote client to escape the storage root with ../ sequences and recursively delete arbitrary writable files or directories. This issue is fixed in version 1.1.6.

## References
- https://github.com/appium/appium/releases/tag/%40appium/storage-plugin%401.1.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58192.json
- https://github.com/appium/appium/security/advisories/GHSA-jwgx-mp9m-jwcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-58192
- https://github.com/appium/appium/commit/5fee01752f2782e96fbe64fd13520b433d4a7535
- https://github.com/appium/appium/pull/22362
