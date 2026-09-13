# [H] SVGO: removeScripts allows executable links through namespace and control-character bypasses

## Summary
Severity: High
Advisory: CVE-2026-84370
Aliases: GHSA-w27v-7q3p-w38r
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84370
Type: osv

## Details
SVGO, short for SVG Optimizer, is a Node.js library and command-line application for optimizing SVG files. From version 1.0.0 until versions 2.8.4, 3.3.5, and 4.1.0, the opt-in removeScripts plugin, named removeScriptElement in versions 2 and 3, incompletely filters executable links in plugins/removeScripts.js and lib/svgo/tools.js. The plugin does not recognize namespace-prefixed SVG anchor elements such as svg:a with href or namespaced *:href values, and it does not remove ASCII tab, line-feed, or carriage-return characters before checking URL schemes. Browsers remove those characters before parsing a scheme, allowing an executable link to pass the plugin's check. When an application processes attacker-controlled SVG input and serves the result in an active browser context, a victim who activates the surviving link can execute script in the SVG's origin, expose data, modify content, or perform actions as the victim. This issue is fixed in versions 2.8.4, 3.3.5, and 4.1.0.

## References
- https://github.com/svg/svgo/releases/tag/v2.8.4
- https://github.com/svg/svgo/releases/tag/v3.3.5
- https://github.com/svg/svgo/releases/tag/v4.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84370.json
- https://github.com/svg/svgo/security/advisories/GHSA-w27v-7q3p-w38r
- https://nvd.nist.gov/vuln/detail/CVE-2026-84370
- https://github.com/svg/svgo/commit/0557385564a5c6c11d76cd934a6cff94451e532c
- https://github.com/svg/svgo/commit/3db3ef33e409a0bc0fdaf255e46c908b00e93bc2
- https://github.com/svg/svgo/commit/994a9f00d79ddec68ce19a1ce9eb8ca08d747e4f
- https://github.com/svg/svgo/pull/2268
- https://github.com/svg/svgo/pull/2269
- https://github.com/svg/svgo/pull/2272
