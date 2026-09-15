# [H] electron-builder's NSIS installer - execute arbitrary code on the target machine (Windows only)

## Summary
Severity: High
Advisory: GHSA-r4pf-3v7r-hh55
CVE: CVE-2024-27303
CWE: CWE-426, CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-r4pf-3v7r-hh55
Type: github-advisory

## Affected
- npm: `app-builder-lib` — affected >=0 <24.13.2

## Details
### Impact
Windows-Only: The NSIS installer makes a system call to open cmd.exe via NSExec in the `.nsh` installer script. NSExec by default searches the current directory of where the installer is located before searching `PATH`. This means that if an attacker can place a malicious executable file named cmd.exe in the same folder as the installer, the installer will run the malicious file.

### Patches
Fixed in https://github.com/electron-userland/electron-builder/pull/8059

### Workarounds
None, it executes at the installer-level before the app is present on the system, so there's no way to check if it exists in a current installer.

### References
https://cwe.mitre.org/data/definitions/426.html
https://cwe.mitre.org/data/definitions/427

## References
- https://github.com/electron-userland/electron-builder/security/advisories/GHSA-r4pf-3v7r-hh55
- https://nvd.nist.gov/vuln/detail/CVE-2024-27303
- https://github.com/electron-userland/electron-builder/pull/8059
- https://github.com/electron-userland/electron-builder/commit/8f4acff3c2d45c1cb07779bb3fe79644408ee387
- https://github.com/electron-userland/electron-builder
