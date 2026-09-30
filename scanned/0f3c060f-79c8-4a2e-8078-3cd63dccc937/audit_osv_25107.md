# [H] eDEX-UI cross-site websocket hijacking vulnerability enables remote command execution

## Summary
Severity: High
Advisory: CVE-2023-30856
Aliases: GHSA-q8xc-f2wf-ffh9
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-30856
Type: osv

## Details
eDEX-UI is a science fiction terminal emulator. Versions 2.2.8 and prior are vulnerable to cross-site websocket hijacking. When running eDEX-UI and browsing the web, a malicious website can connect to eDEX's internal terminal control websocket, and send arbitrary commands to the shell. The project has been archived since 2021, and as of time of publication there are no plans to patch this issue and release a new version. Some workarounds are available, including shutting down eDEX-UI when browsing the web and ensuring the eDEX terminal runs with lowest possible privileges.

## References
- https://christian-schneider.net/CrossSiteWebSocketHijacking.html
- https://github.com/GitSquared/edex-ui/blob/04a00c4079908788b371c6ecdefff96d0d9950f8/src/classes/terminal.class.js#L458
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30856.json
- https://github.com/GitSquared/edex-ui/security/advisories/GHSA-q8xc-f2wf-ffh9
- https://nvd.nist.gov/vuln/detail/CVE-2023-30856
