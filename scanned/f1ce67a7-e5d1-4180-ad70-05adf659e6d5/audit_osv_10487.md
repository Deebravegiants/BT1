# [C] CVE-2017-16151

## Summary
Severity: Critical
Advisory: CVE-2017-16151
Aliases: GHSA-4w88-rjj3-x7wp
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-07
Source: https://osv.dev/vulnerability/CVE-2017-16151
Type: osv

## Details
Based on details posted by the ElectronJS team; A remote code execution vulnerability has been discovered in Google Chromium that affects all recent versions of Electron. Any Electron app that accesses remote content is vulnerable to this exploit, regardless of whether the [sandbox option](https://electron.atom.io/docs/api/sandbox-option) is enabled.

## References
- https://nodesecurity.io/advisories/539
- https://electron.atom.io/blog/2017/09/27/chromium-rce-vulnerability-fix
