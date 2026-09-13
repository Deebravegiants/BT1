# [M] CVE-2018-14036

## Summary
Severity: Medium
Advisory: CVE-2018-14036
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-14036
Type: osv

## Details
Directory Traversal with ../ sequences occurs in AccountsService before 0.6.50 because of an insufficient path check in user_change_icon_file_authorized_cb() in user.c.

## References
- http://www.securityfocus.com/bid/104757
- https://bugzilla.suse.com/show_bug.cgi?id=1099699
- https://cgit.freedesktop.org/accountsservice/commit/?id=f9abd359f71a5bce421b9ae23432f539a067847a
- https://bugs.freedesktop.org/show_bug.cgi?id=107085
- http://www.openwall.com/lists/oss-security/2018/07/02/2
