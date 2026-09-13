# [M] CVE-2015-20109

## Summary
Severity: Medium
Advisory: CVE-2015-20109
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-25
Source: https://osv.dev/vulnerability/CVE-2015-20109
Type: osv

## Details
end_pattern (called from internal_fnmatch) in the GNU C Library (aka glibc or libc6) before 2.22 might allow context-dependent attackers to cause a denial of service (application crash), as demonstrated by use of the fnmatch library function with the **(!() pattern. NOTE: this is not the same as CVE-2015-8984; also, some Linux distributions have fixed CVE-2015-8984 but have not fixed this additional fnmatch issue.

## References
- https://security.netapp.com/advisory/ntap-20230731-0009/
- https://sourceware.org/bugzilla/show_bug.cgi?id=18036
- https://sourceware.org/bugzilla/show_bug.cgi?id=18036
