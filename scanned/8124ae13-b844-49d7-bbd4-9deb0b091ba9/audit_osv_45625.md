# [H] JLSEC-2026-14

## Summary
Severity: High
Advisory: JLSEC-2026-14
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/JLSEC-2026-14
Type: osv

## Affected
- Julia: `patch_jll` — affected >=0 <2.8.0+0

## Details
An issue was discovered in GNU patch through 2.7.6. There is a segmentation fault, associated with a NULL pointer dereference, leading to a denial of service in the `intuit_diff_type` function in pch.c, aka a "mangled rename" issue.

## References
- http://www.securityfocus.com/bid/103044
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=f290f48a621867084884bfff87f8093c15195e6a
- https://savannah.gnu.org/bugs/index.php?53132
- https://security.gentoo.org/glsa/201904-17
- https://usn.ubuntu.com/3624-1/
