# [H] CVE-2022-39046

## Summary
Severity: High
Advisory: CVE-2022-39046
CVSS: 7.5 (CVSS:3.1/AC:L/AV:N/A:N/C:H/I:N/PR:N/S:U/UI:N)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-39046
Type: osv

## Details
An issue was discovered in the GNU C Library (glibc) 2.36. When the syslog function is passed a crafted input string larger than 1024 bytes, it reads uninitialized memory from the heap and prints it to the target log file, potentially revealing a portion of the contents of the heap.

## References
- http://packetstormsecurity.com/files/176932/glibc-syslog-Heap-Based-Buffer-Overflow.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39046.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-39046
- https://security.gentoo.org/glsa/202310-03
- https://security.netapp.com/advisory/ntap-20221104-0002/
- https://sourceware.org/bugzilla/show_bug.cgi?id=29536
- http://seclists.org/fulldisclosure/2024/Feb/3
- http://www.openwall.com/lists/oss-security/2024/01/30/6
- http://www.openwall.com/lists/oss-security/2024/01/30/8
