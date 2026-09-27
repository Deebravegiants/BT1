# [H] CVE-2018-13054

## Summary
Severity: High
Advisory: CVE-2018-13054
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/CVE-2018-13054
Type: osv

## Details
An issue was discovered in Cinnamon 1.9.2 through 3.8.6. The cinnamon-settings-users.py GUI runs as root and allows configuration of (for example) other users' icon files in _on_face_browse_menuitem_activated and _on_face_menuitem_activated. These icon files are written to the respective user's $HOME/.face location. If an unprivileged user prepares a symlink pointing to an arbitrary location, then this location will be overwritten with the icon content.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00011.html
- https://bugzilla.suse.com/show_bug.cgi?id=1083067
- https://github.com/linuxmint/Cinnamon/pull/7683
