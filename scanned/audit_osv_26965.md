# [M] Glibc: integer overflow in __vsyslog_internal()

## Summary
Severity: Medium
Advisory: CVE-2023-6780
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2023-6780
Type: osv

## Details
An integer overflow was found in the __vsyslog_internal function of the glibc library. This function is called by the syslog and vsyslog functions. This issue occurs when these functions are called with a very long message, leading to an incorrect calculation of the buffer size to store the message, resulting in undefined behavior. This issue affects glibc 2.37 and newer.

## References
- http://packetstormsecurity.com/files/176932/glibc-syslog-Heap-Based-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2024/Feb/3
- https://access.redhat.com/downloads/content/package-browser/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D2FIH77VHY3KCRROCXOT6L27WMZXSJ2G/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MWQ6BZJ6CV5UAW4VZSKJ6TO4KIW2KWAQ/
- https://packages.fedoraproject.org/
- https://www.openwall.com/lists/oss-security/2024/01/30/6
- https://www.qualys.com/2024/01/30/cve-2023-6246/syslog.txt
- https://access.redhat.com/security/cve/CVE-2023-6780
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6780.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6780
- https://security.gentoo.org/glsa/202402-01
- https://security.netapp.com/advisory/ntap-20250207-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=2254396
