# [H] CVE-2016-7162

## Summary
Severity: High
Advisory: CVE-2016-7162
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-7162
Type: osv

## Details
The _g_file_remove_directory function in file-utils.c in File Roller 3.5.4 through 3.20.2 allows remote attackers to delete arbitrary files via a symlink attack on a folder in an archive.

## References
- http://ftp.gnome.org/mirror/gnome.org/sources/file-roller/3.21/file-roller-3.21.90.news
- http://ftp.gnome.org/mirror/gnome.org/sources/file-roller/3.20/file-roller-3.20.3.news
- http://www.openwall.com/lists/oss-security/2016/09/08/4
- http://www.securityfocus.com/bid/92896
- http://www.ubuntu.com/usn/USN-3074-1
- https://bugzilla.gnome.org/show_bug.cgi?id=698554
- https://git.gnome.org/browse/file-roller/commit/?id=f70be1f41688859ec8dbe266df35a1839ceb96c5
