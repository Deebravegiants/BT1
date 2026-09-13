# [H] CVE-2015-1396

## Summary
Severity: High
Advisory: CVE-2015-1396
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2015-1396
Type: osv

## Details
A Directory Traversal vulnerability exists in the GNU patch before 2.7.4. A remote attacker can write to arbitrary files via a symlink attack in a patch file. NOTE: this issue exists because of an incomplete fix for CVE-2015-1196.

## References
- http://www.securityfocus.com/bid/75358
- http://www.ubuntu.com/usn/USN-2651-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1186764
- http://www.openwall.com/lists/oss-security/2015/01/27/29
