# [H] Git CMD erroneously executes `doskey.exe` in the current directory, if it exists

## Summary
Severity: High
Advisory: CVE-2023-29012
Aliases: GHSA-gq5x-v87v-8f7g
CVSS: 7.2 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2023-29012
Type: osv

## Details
Git for Windows is the Windows port of Git. Prior to version 2.40.1, any user of Git CMD who starts the command in an untrusted directory is impacted by an Uncontrolles Search Path Element vulnerability. Maliciously-placed `doskey.exe` would be executed silently upon running Git CMD. The problem has been patched in Git for Windows v2.40.1. As a workaround, avoid using Git CMD or, if using Git CMD, avoid starting it in an untrusted directory.

## References
- https://github.com/git-for-windows/git/releases/tag/v2.40.1.windows.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29012.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-gq5x-v87v-8f7g
- https://nvd.nist.gov/vuln/detail/CVE-2023-29012
