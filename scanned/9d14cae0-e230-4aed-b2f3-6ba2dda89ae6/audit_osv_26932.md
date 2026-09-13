# [H] Glibc: heap-based buffer overflow in __vsyslog_internal()

## Summary
Severity: High
Advisory: CVE-2023-6246
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2023-6246
Type: osv

## Details
A heap-based buffer overflow was found in the __vsyslog_internal function of the glibc library. This function is called by the syslog and vsyslog functions. This issue occurs when the openlog function was not called, or called with the ident argument set to NULL, and the program name (the basename of argv[0]) is bigger than 1024 bytes, resulting in an application crash or local privilege escalation. This issue affects glibc 2.36 and newer.

## References
- http://packetstormsecurity.com/files/176931/glibc-qsort-Out-Of-Bounds-Read-Write.html
- http://packetstormsecurity.com/files/176932/glibc-syslog-Heap-Based-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2024/Feb/3
- http://seclists.org/fulldisclosure/2024/Feb/5
- https://access.redhat.com/downloads/content/package-browser/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D2FIH77VHY3KCRROCXOT6L27WMZXSJ2G/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MWQ6BZJ6CV5UAW4VZSKJ6TO4KIW2KWAQ/
- https://packages.fedoraproject.org/
- https://www.openwall.com/lists/oss-security/2024/01/30/6
- https://www.qualys.com/2024/01/30/cve-2023-6246/syslog.txt
- https://access.redhat.com/security/cve/CVE-2023-6246
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6246.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6246
- https://security.gentoo.org/glsa/202402-01
- https://security.netapp.com/advisory/ntap-20240216-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=2249053
