# [M] Field `file_table` of `struct module *module` is uninitialized

## Summary
Severity: Medium
Advisory: CVE-2023-25585
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-14
Source: https://osv.dev/vulnerability/CVE-2023-25585
Type: osv

## Details
A flaw was found in Binutils. The use of an uninitialized field in the struct module *module may lead to application crash and local denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=65cf035b8dc1df5d8020e0b1449514a3c42933e7
- https://access.redhat.com/security/cve/CVE-2023-25585
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25585.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25585
- https://security.netapp.com/advisory/ntap-20231103-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2167498
- https://sourceware.org/bugzilla/show_bug.cgi?id=29892
