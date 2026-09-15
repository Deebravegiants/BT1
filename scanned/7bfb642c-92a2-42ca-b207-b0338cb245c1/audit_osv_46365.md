# [C] CVE-2005-3590

## Summary
Severity: Critical
Advisory: CVE-2005-3590
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-10
Source: https://osv.dev/vulnerability/CVE-2005-3590
Type: osv

## Details
The getgrouplist function in the GNU C library (glibc) before version 2.3.5, when invoked with a zero argument, writes to the passed pointer even if the specified array size is zero, leading to a buffer overflow and potentially allowing attackers to corrupt memory.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=661
- https://sourceware.org/bugzilla/show_bug.cgi?id=661
- https://sourceware.org/bugzilla/show_bug.cgi?id=661
- http://www.securityfocus.com/bid/107871
- https://support.f5.com/csp/article/K12740406
