# [H] CVE-2018-6951

## Summary
Severity: High
Advisory: CVE-2018-6951
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-6951
Type: osv

## Details
An issue was discovered in GNU patch through 2.7.6. There is a segmentation fault, associated with a NULL pointer dereference, leading to a denial of service in the intuit_diff_type function in pch.c, aka a "mangled rename" issue.

## References
- http://www.securityfocus.com/bid/103044
- https://security.gentoo.org/glsa/201904-17
- https://usn.ubuntu.com/3624-1/
- https://savannah.gnu.org/bugs/index.php?53132
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=f290f48a621867084884bfff87f8093c15195e6a
