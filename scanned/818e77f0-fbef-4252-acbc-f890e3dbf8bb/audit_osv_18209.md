# [H] CVE-2020-25019

## Summary
Severity: High
Advisory: CVE-2020-25019
Aliases: GHSA-x4h8-fhrp-pm3p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-08-29
Source: https://osv.dev/vulnerability/CVE-2020-25019
Type: osv

## Details
jitsi-meet-electron (aka Jitsi Meet Electron) before 2.3.0 calls the Electron shell.openExternal function without verifying that the URL is for an http or https resource, in some circumstances.

## References
- https://github.com/jitsi/jitsi-meet-electron/releases/tag/v2.3.0
- https://github.com/jitsi/jitsi-meet-electron/security/advisories/GHSA-x4h8-fhrp-pm3p
- https://github.com/jitsi/security-advisories/blob/master/advisories/JSA-2020-0001.md
- https://github.com/jitsi/jitsi-meet-electron/commit/ca1eb702507fdc4400fe21c905a9f85702f92a14
- https://security.stackexchange.com/questions/225799
