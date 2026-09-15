# [M] CVE-2018-19044

## Summary
Severity: Medium
Advisory: CVE-2018-19044
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19044
Type: osv

## Details
keepalived 2.0.8 didn't check for pathnames with symlinks when writing data to a temporary file upon a call to PrintData or PrintStats. This allowed local users to overwrite arbitrary files if fs.protected_symlinks is set to 0, as demonstrated by a symlink from /tmp/keepalived.data or /tmp/keepalived.stats to /etc/passwd.

## References
- https://access.redhat.com/errata/RHSA-2019:2285
- https://security.gentoo.org/glsa/201903-01
- https://bugzilla.suse.com/show_bug.cgi?id=1015141
- https://github.com/acassen/keepalived/commit/04f2d32871bb3b11d7dc024039952f2fe2750306
- https://github.com/acassen/keepalived/issues/1048
