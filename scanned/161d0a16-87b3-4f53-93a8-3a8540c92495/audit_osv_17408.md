# [M] CVE-2020-15096

## Summary
Severity: Medium
Advisory: CVE-2020-15096
Aliases: GHSA-6vrv-94jv-crrg
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-15096
Type: osv

## Details
In Electron before versions 6.1.1, 7.2.4, 8.2.4, and 9.0.0-beta21, there is a context isolation bypass, meaning that code running in the main world context in the renderer can reach into the isolated Electron context and perform privileged actions. Apps using "contextIsolation" are affected. There are no app-side workarounds, you must update your Electron version to be protected. This is fixed in versions 6.1.1, 7.2.4, 8.2.4, and 9.0.0-beta21.

## References
- https://github.com/electron/electron/security/advisories/GHSA-6vrv-94jv-crrg
- https://www.electronjs.org/releases/stable?page=3#release-notes-for-v824
