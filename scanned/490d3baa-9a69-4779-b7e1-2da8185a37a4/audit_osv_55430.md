# [H] Git GUI can create and overwrite files for which the user has write permission

## Summary
Severity: High
Advisory: CVE-2025-46835
Aliases: GHSA-xfx7-68v4-v8fg
CVSS: 8.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-46835
Type: osv

## Details
Git GUI allows you to use the Git source control management tools via a GUI. When a user clones an untrusted repository and is tricked into editing a file located in a maliciously named directory in the repository, then Git GUI can create and overwrite files for which the user has write permission. This vulnerability is fixed in 2.43.7, 2.44.4, 2.45.4, 2.46.4, 2.47.3, 2.48.2, 2.49.1, and 2.50.1.

## References
- http://www.openwall.com/lists/oss-security/2025/07/08/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46835.json
- https://github.com/j6t/git-gui/compare/dcda716dbc9c90bcac4611bd1076747671ee0906..a437f5bc93330a70b42a230e52f3bd036ca1b1da
- https://github.com/j6t/git-gui/security/advisories/GHSA-xfx7-68v4-v8fg
- https://lists.debian.org/debian-lts-announce/2025/10/msg00003.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-46835
