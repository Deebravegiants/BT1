# [H] Malicious directory junction can cause WiX RemoveFoldersEx to possibly delete elevated files

## Summary
Severity: High
Advisory: GHSA-jx4p-m4wm-vvjg
CVE: CVE-2024-29188
CWE: CWE-59
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-jx4p-m4wm-vvjg
Type: github-advisory

## Affected
- NuGet: `wix` — affected >=0 <3.14.1
- NuGet: `wix` — affected >=4.0.0 <4.0.5
- NuGet: `WixToolset.Util.wixext` — affected >=0 <4.0.5

## Details
### Summary
The custom action behind WiX's `RemoveFolderEx` functionality could allow a standard user to delete protected directories.

### Details
`RemoveFolderEx` deletes an entire directory tree during installation or uninstallation. It does so by recursing every subdirectory starting at a specified directory and adding each subdirectory to the list of directories Windows Installer should delete. If the setup author instructed `RemoveFolderEx` to delete a per-user folder from a per-machine installer, an attacker could create a directory junction in that per-user folder pointing to a per-machine, protected directory. Windows Installer, when executing the per-machine installer after approval by an administrator, would delete the target of the directory junction.

## References
- https://github.com/wixtoolset/issues/security/advisories/GHSA-jx4p-m4wm-vvjg
- https://nvd.nist.gov/vuln/detail/CVE-2024-29188
- https://github.com/wixtoolset/wix/commit/2e5960b575881567a8807e6b8b9c513138b19742
- https://github.com/wixtoolset/wix3/commit/93eeb5f6835776694021f66d4226c262c67d487a
- https://github.com/wixtoolset/issues
