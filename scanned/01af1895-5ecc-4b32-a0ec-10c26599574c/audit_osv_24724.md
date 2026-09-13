# [M] Field `the_bfd` of `asymbol` is uninitialized in function `bfd_mach_o_get_synthetic_symtab`

## Summary
Severity: Medium
Advisory: CVE-2023-25588
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-14
Source: https://osv.dev/vulnerability/CVE-2023-25588
Type: osv

## Details
A flaw was found in Binutils. The field `the_bfd` of `asymbol`struct is uninitialized in the `bfd_mach_o_get_synthetic_symtab` function, which may lead to an application crash and local denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=d12f8998d2d086f0a6606589e5aedb7147e6f2f1
- https://access.redhat.com/security/cve/CVE-2023-25588
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25588.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25588
- https://security.netapp.com/advisory/ntap-20231103-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2167505
- https://sourceware.org/bugzilla/show_bug.cgi?id=29677
