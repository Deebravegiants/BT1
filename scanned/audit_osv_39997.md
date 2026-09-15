# [C] CVE-2026-48831

## Summary
Severity: Critical
Advisory: CVE-2026-48831
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/AU:N/V:D/U:Clear)
Published: 2026-05-24
Source: https://osv.dev/vulnerability/CVE-2026-48831
Type: osv

## Details
Wine ships a .desktop file that registers itself as a MIME handler for EXE files and several other Windows executable file types. In some configurations, handling of an EXE file causes that file to be blindly executed with the permissions of the invoker. This allows escaping Flatpak and Snap sandboxes, because MIME handlers are not intended for use by code interpreters and loaders. NOTE: some parties feel that this is not a bug to be addressed in Wine, because there is no known solution that avoids a severe loss of usability (Wine could be a binfmt-misc handler, but binfmt-misc does not exist on all platforms supported by Wine).

## References
- http://www.openwall.com/lists/oss-security/2026/05/25/1
- https://bugs.winehq.org/show_bug.cgi?id=59767
- https://www.openwall.com/lists/oss-security/2026/05/19/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48831.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48831
- https://gitlab.winehq.org/wine/wine
