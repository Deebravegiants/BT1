# [M] CVE-2023-1972

## Summary
Severity: Medium
Advisory: CVE-2023-1972
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-1972
Type: osv

## Details
A potential heap based buffer overflow was found in _bfd_elf_slurp_version_tables() in bfd/elf.c. This may lead to loss of availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1972.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1972
- https://security.gentoo.org/glsa/202309-15
- https://bugzilla.redhat.com/show_bug.cgi?id=2185646
- https://sourceware.org/bugzilla/show_bug.cgi?id=30285
