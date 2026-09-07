# [H] electron-updater Code Signing Bypass on Windows

## Summary
Severity: High
Advisory: GHSA-9jxc-qjr9-vjxq
CVE: CVE-2024-39698
CWE: CWE-154, CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-09
Source: https://github.com/advisories/GHSA-9jxc-qjr9-vjxq
Type: github-advisory

## Affected
- npm: `electron-updater` — affected >=0 <6.3.0-alpha.6

## Details
### Observations
The file `packages/electron-updater/src/windowsExecutableCodeSignatureVerifier.ts` implements the signature validation routine for Electron applications on Windows. It executes the following command in a new shell (`process.env.ComSpec` on Windows, usually `C:\Windows\System32\cmd.exe`):

https://github.com/electron-userland/electron-builder/blob/140e2f0eb0df79c2a46e35024e96d0563355fc89/packages/electron-updater/src/windowsExecutableCodeSignatureVerifier.ts#L35-L41

Because of the surrounding shell, a first pass by `cmd.exe` expands any environment variable found in command-line above.

### Exploitation

This creates a situation where `verifySignature()` can be tricked into validating the certificate of a different file than the one that was just downloaded. If the step is successful, the malicious update will be executed even if its signature is invalid. 

### Impact

This attack assumes a compromised update manifest (server compromise, Man-in-the-Middle attack if fetched over HTTP, Cross-Site Scripting to point the application to a malicious updater server, etc.).

### Patch

This vulnerability was patched in #8295, by comparing the path in the output of `Get-AuthenticodeSignature` with the intended one. The patch is available starting from 6.3.0-alpha.6.

## References
- https://github.com/electron-userland/electron-builder/security/advisories/GHSA-9jxc-qjr9-vjxq
- https://nvd.nist.gov/vuln/detail/CVE-2024-39698
- https://github.com/electron-userland/electron-builder/pull/8295
- https://github.com/electron-userland/electron-builder/commit/ac2e6a25aa491c1ef5167a552c19fc2085cd427f
- https://github.com/electron-userland/electron-builder
- https://github.com/electron-userland/electron-builder/blob/140e2f0eb0df79c2a46e35024e96d0563355fc89/packages/electron-updater/src/windowsExecutableCodeSignatureVerifier.ts#L35-L41
