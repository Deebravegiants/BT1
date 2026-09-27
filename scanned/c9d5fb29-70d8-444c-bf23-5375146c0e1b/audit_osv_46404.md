# [H] CVE-2009-3289

## Summary
Severity: High
Advisory: CVE-2009-3289
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2009-09-22
Source: https://osv.dev/vulnerability/CVE-2009-3289
Type: osv

## Details
The g_file_copy function in glib 2.0 sets the permissions of a target file to the permissions of a symbolic link (777), which allows user-assisted local users to modify files of other users, as demonstrated by using Nautilus to modify the permissions of the user home directory.

## References
- http://lists.opensuse.org/opensuse-security-announce/2010-04/msg00006.html
- http://secunia.com/advisories/39656
- http://www.openwall.com/lists/oss-security/2009/09/08/8
- https://bugs.launchpad.net/ubuntu/+source/glib2.0/+bug/418135
- https://bugzilla.gnome.org/show_bug.cgi?id=593406
- http://www.vupen.com/english/advisories/2010/1001
- https://bugs.launchpad.net/ubuntu/+source/glib2.0/+bug/418135
- https://bugzilla.gnome.org/show_bug.cgi?id=593406
