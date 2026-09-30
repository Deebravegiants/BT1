# [M] GoCD Windows installations outside default location inadequately restrict installation file permissions

## Summary
Severity: Medium
Advisory: CVE-2022-36088
Aliases: GHSA-gpv4-xqhc-5vcj
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-09-07
Source: https://osv.dev/vulnerability/CVE-2022-36088
Type: osv

## Details
GoCD is a continuous delivery server. Windows installations via either the server or agent installers for GoCD prior to 22.2.0 do not adequately restrict permissions when installing outside of the default location. This could allow a malicious user with local access to the server GoCD Server or Agent are installed on to modify executables or components of the installation. This does not affect zip file-based installs, installations to other platforms, or installations inside `Program Files` or `Program Files (x86)`. This issue is fixed in GoCD 22.2.0 installers. As a workaround, if the server or agent is installed outside of `Program Files (x86)`, verify the the permission of the Server or Agent installation directory to ensure the `Everyone` user group does not have `Full Control`, `Modify` or `Write` permissions.

## References
- https://github.com/gocd/gocd/releases/tag/22.2.0
- https://www.gocd.org/releases/#22-2-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36088.json
- https://github.com/gocd/gocd/security/advisories/GHSA-gpv4-xqhc-5vcj
- https://nvd.nist.gov/vuln/detail/CVE-2022-36088
- https://github.com/gocd/gocd/commit/96add9605096ab50c5cd4c229be1d503aff506a6
