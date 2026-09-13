# [H] CVE-2016-10026

## Summary
Severity: High
Advisory: CVE-2016-10026
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-10026
Type: osv

## Details
ikiwiki 3.20161219 does not properly check if a revision changes the access permissions for a page on sites with the git and recentchanges plugins and the CGI interface enabled, which allows remote attackers to revert certain changes by leveraging permissions to change the page before the revision was made.

## References
- http://www.openwall.com/lists/oss-security/2016/12/21/3
- http://www.openwall.com/lists/oss-security/2016/12/29/3
- https://ikiwiki.info/security/#index46h2
- http://www.debian.org/security/2017/dsa-3760
- http://ikiwiki.info/bugs/rcs_revert_can_bypass_authorization_if_affected_files_were_renamed/
