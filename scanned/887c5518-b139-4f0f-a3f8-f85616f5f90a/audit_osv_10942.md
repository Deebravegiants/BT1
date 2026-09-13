# [H] CVE-2017-5333

## Summary
Severity: High
Advisory: CVE-2017-5333
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-04
Source: https://osv.dev/vulnerability/CVE-2017-5333
Type: osv

## Details
Integer overflow in the extract_group_icon_cursor_resource function in b/wrestool/extract.c in icoutils before 0.31.1 allows local users to cause a denial of service (process crash) or execute arbitrary code via a crafted executable file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00026.html
- http://rhn.redhat.com/errata/RHSA-2017-0837.html
- http://www.debian.org/security/2017/dsa-3765
- http://www.securityfocus.com/bid/95678
- http://www.ubuntu.com/usn/USN-3178-1
- http://www.openwall.com/lists/oss-security/2017/01/11/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1412259
- https://git.savannah.gnu.org/cgit/icoutils.git/commit/?id=1a108713ac26215c7568353f6e02e727e6d4b24a
