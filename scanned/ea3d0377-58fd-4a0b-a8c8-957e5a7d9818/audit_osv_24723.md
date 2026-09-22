# [M] Local variable `ch_type` in function `bfd_init_section_decompress_status` can be uninitialized

## Summary
Severity: Medium
Advisory: CVE-2023-25586
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-14
Source: https://osv.dev/vulnerability/CVE-2023-25586
Type: osv

## Details
A flaw was found in Binutils. A logic fail in the bfd_init_section_decompress_status function may lead to the use of an uninitialized variable that can cause a crash and local denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=5830876a0cca17bef3b2d54908928e72cca53502
- https://access.redhat.com/security/cve/CVE-2023-25586
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25586.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25586
- https://security.netapp.com/advisory/ntap-20231103-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2167502
- https://sourceware.org/bugzilla/show_bug.cgi?id=29855
