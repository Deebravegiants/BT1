# [M] Binutils: out-of-bounds read in xcoff relocation processing in gnu binutils bfd library

## Summary
Severity: Medium
Advisory: CVE-2026-4647
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-4647
Type: osv

## Details
A flaw was found in the GNU Binutils BFD library, a widely used component for handling binary files such as object files and executables. The issue occurs when processing specially crafted XCOFF object files, where a relocation type value is not properly validated before being used. This can cause the program to read memory outside of intended bounds. As a result, affected tools may crash or expose unintended memory contents, leading to denial-of-service or limited information disclosure risks.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:33527
- https://access.redhat.com/errata/RHSA-2026:39022
- https://access.redhat.com/security/cve/CVE-2026-4647
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4647.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4647
- https://bugzilla.redhat.com/show_bug.cgi?id=2450302
- https://sourceware.org/bugzilla/show_bug.cgi?id=33919
