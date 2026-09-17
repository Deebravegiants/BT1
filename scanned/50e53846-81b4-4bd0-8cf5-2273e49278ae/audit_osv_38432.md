# [M] flatpak-builder has a path traversal leading to arbitrary file read on host when installing licence files

## Summary
Severity: Medium
Advisory: CVE-2026-39977
Aliases: GHSA-6gm9-3g7m-3965
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39977
Type: osv

## Details
flatpak-builder is a tool to build flatpaks from source. From 1.4.5 to before 1.4.8, the license-files manifest key takes an array of paths to user defined licence files relative to the source directory of the module. The paths from that array are resolved using g_file_resolve_relative_path() and validated to stay inside the source directory using two checks - g_file_get_relative_path() which does not resolve symlinks and g_file_query_file_type() with G_FILE_QUERY_INFO_NOFOLLOW_SYMLINKS which only applies to the final path component. The copy operation runs on host. This can be exploited by using a crafted manifest and/or source to read arbitrary files from the host and capture them into the build output. This vulnerability is fixed in 1.4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39977.json
- https://github.com/flatpak/flatpak-builder/security/advisories/GHSA-6gm9-3g7m-3965
- https://nvd.nist.gov/vuln/detail/CVE-2026-39977
