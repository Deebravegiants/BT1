# [H] Electron vulnerable to remote command execution

## Summary
Severity: High
Advisory: GHSA-7fv9-m79r-j9x8
CVE: CVE-2017-12581
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7fv9-m79r-j9x8
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <1.6.8

## Details
Electron before 1.6.8 allows remote command execution because of a `nodeIntegration` bypass vulnerability. This also affects all applications that bundle Electron code equivalent to 1.6.8 or earlier. Bypassing the Same Origin Policy (SOP) is a precondition; however, recent Electron versions do not have strict SOP enforcement. Combining an SOP bypass with a privileged URL internally used by Electron, it was possible to execute native Node.js primitives in order to run OS commands on the user's host. Specifically, a `chrome-devtools://devtools/bundled/inspector.html` window could be used to eval a Node.js `child_process.execFile` API call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12581
- https://github.com/electron/electron/commit/05b6d91bf4c1e0ee65eeef70cd5d1bd1df125644
- https://blog.doyensec.com/2017/08/03/electron-framework-security.html
- https://doyensec.com/resources/us-17-Carettoni-Electronegativity-A-Study-Of-Electron-Security.pdf
- https://github.com/electron/electron
