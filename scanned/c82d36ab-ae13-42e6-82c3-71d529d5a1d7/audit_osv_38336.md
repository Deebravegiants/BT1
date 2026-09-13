# [M] CVE-2026-3904

## Summary
Severity: Medium
Advisory: CVE-2026-3904
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-3904
Type: osv

## Details
Calling NSS-backed functions that support caching via nscd may call the 
nscd client side code and in the GNU C Library version 2.36 under high 
load on x86_64 systems, the client may call memcmp on inputs that are 
concurrently modified by other processes or threads and crash.




The nscd client in the GNU C Library uses the memcmp function with 
inputs that may be concurrently modified by another thread, potentially 
resulting in spurious cache misses, which in itself is not a security 
issue.  However in the GNU C Library version 2.36 an optimized 
implementation of memcmp was introduced for x86_64 which could crash 
when invoked with such undefined behaviour, turning this into a 
potential crash of the nscd client and the application that uses it. 
This implementation was backported to the 2.35 branch, making the nscd 
client in that branch vulnerable as well.  Subsequently, the fix for 
this issue was backported to all vulnerable branches in the GNU C 
Library repository.


It is advised that distributions that may have cherry-picked the memcpy 
SSE2 optimization in their copy of the GNU C Library, also apply the fix 
to avoid the potential crash in the nscd client.

## References
- http://www.openwall.com/lists/oss-security/2026/03/11/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://sourceware.org/git/?p=glibc.git;a=commit;h=8804157ad9da39631703b92315460808eac86b0c
- https://sourceware.org/git/?p=glibc.git;a=commit;h=b712be52645282c706a5faa038242504feb06db5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3904.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3904
- https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=advisories/GLIBC-SA-2026-0004;hb=HEAD
- https://sourceware.org/bugzilla/show_bug.cgi?id=29863
