# [H] CVE-2018-15685

## Summary
Severity: High
Advisory: CVE-2018-15685
Aliases: GHSA-hv9c-qwqg-qj3v
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-23
Source: https://osv.dev/vulnerability/CVE-2018-15685
Type: osv

## Details
GitHub Electron 1.7.15, 1.8.7, 2.0.7, and 3.0.0-beta.6, in certain scenarios involving IFRAME elements and "nativeWindowOpen: true" or "sandbox: true" options, is affected by a WebPreferences vulnerability that can be leveraged to perform remote code execution.

## References
- https://electronjs.org/blog/web-preferences-fix
- https://www.exploit-db.com/exploits/45272/
