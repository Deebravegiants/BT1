# [M] CVE-2025-32807

## Summary
Severity: Medium
Advisory: CVE-2025-32807
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-04-11
Source: https://osv.dev/vulnerability/CVE-2025-32807
Type: osv

## Details
A path traversal vulnerability in FusionDirectory before 1.5 allows remote attackers to read arbitrary files on the host that end with .png (and .svg or .xpm for some configurations) via the icon parameter of a GET request to geticon.php.

## References
- https://gitlab.fusiondirectory.org/fusiondirectory/fd/-/blob/e9304844fb5c8ce4a9af9e26858af5e22e15b9bd/include/class_IconTheme.inc#L233-237
- https://gitlab.fusiondirectory.org/fusiondirectory/fd/-/blob/e9304844fb5c8ce4a9af9e26858af5e22e15b9bd/Changelog.md?plain=1#L112
- https://gitlab.fusiondirectory.org/fusiondirectory/fd/-/commit/9edefd0b367450d665a141c5e94db8a06d208556
