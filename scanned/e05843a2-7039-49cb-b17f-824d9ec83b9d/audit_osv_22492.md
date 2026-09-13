# [H] Git for Windows' installer can be tricked into executing an untrusted binary

## Summary
Severity: High
Advisory: CVE-2022-31012
Aliases: GHSA-gjrj-fxvp-hjj2
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-07-12
Source: https://osv.dev/vulnerability/CVE-2022-31012
Type: osv

## Details
Git for Windows is a fork of Git that contains Windows-specific patches. This vulnerability in versions prior to 2.37.1 lets Git for Windows' installer execute a binary into `C:\mingw64\bin\git.exe` by mistake. This only happens upon a fresh install, not when upgrading Git for Windows. A patch is included in version 2.37.1. Two workarounds are available. Create the `C:\mingw64` folder and remove read/write access from this folder, or disallow arbitrary authenticated users to create folders in `C:\`.

## References
- https://github.com/git-for-windows/git/releases/tag/v2.37.1.windows.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31012.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-gjrj-fxvp-hjj2
- https://nvd.nist.gov/vuln/detail/CVE-2022-31012
