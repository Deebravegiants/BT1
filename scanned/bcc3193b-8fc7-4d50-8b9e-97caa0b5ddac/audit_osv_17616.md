# [H] CVE-2020-1751

## Summary
Severity: High
Advisory: CVE-2020-1751
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-17
Source: https://osv.dev/vulnerability/CVE-2020-1751
Type: osv

## Details
An out-of-bounds write vulnerability was found in glibc before 2.31 when handling signal trampolines on PowerPC. Specifically, the backtrace function did not properly check the array bounds when storing the frame address, resulting in a denial of service or potential code execution. The highest threat from this vulnerability is to system availability.

## References
- https://security.gentoo.org/glsa/202006-04
- https://security.netapp.com/advisory/ntap-20200430-0002/
- https://usn.ubuntu.com/4416-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25423
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1751
