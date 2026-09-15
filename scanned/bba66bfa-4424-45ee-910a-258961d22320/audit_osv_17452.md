# [M] CVE-2020-15215

## Summary
Severity: Medium
Advisory: CVE-2020-15215
Aliases: GHSA-56pc-6jqp-xqj8
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-15215
Type: osv

## Details
Electron before versions 11.0.0-beta.6, 10.1.2, 9.3.1 or 8.5.2 is vulnerable to a context isolation bypass. Apps using both `contextIsolation` and `sandbox: true` are affected. Apps using both `contextIsolation` and `nodeIntegrationInSubFrames: true` are affected. This is a context isolation bypass, meaning that code running in the main world context in the renderer can reach into the isolated Electron context and perform privileged actions.

## References
- https://github.com/electron/electron/security/advisories/GHSA-56pc-6jqp-xqj8
