# [M] CVE-2025-8058

## Summary
Severity: Medium
Advisory: CVE-2025-8058
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:P/VC:L/VI:L/VA:H/SC:L/SI:L/SA:H)
Published: 2025-07-23
Source: https://osv.dev/vulnerability/CVE-2025-8058
Type: osv

## Details
The regcomp function in the GNU C library version from 2.4 to 2.41 is 
subject to a double free if some previous allocation fails. It can be 
accomplished either by a malloc failure or by using an interposed malloc
 that injects random malloc failures. The double free can allow buffer 
manipulation depending of how the regex is constructed. This issue 
affects all architectures and ABIs supported by the GNU C library.

## References
- http://www.openwall.com/lists/oss-security/2025/07/23/1
- https://sourceware.org/git/?p=glibc.git;a=commit;h=3ff17af18c38727b88d9115e536c069e6b5d601f
- https://www.gnu.org/software/libc/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8058.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-8058
- https://sourceware.org/bugzilla/show_bug.cgi?id=33185
- https://sourceware.org/git/?p=glibc.git
