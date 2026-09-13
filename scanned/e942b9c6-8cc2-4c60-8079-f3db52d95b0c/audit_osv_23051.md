# [M] CVE-2022-4285

## Summary
Severity: Medium
Advisory: CVE-2022-4285
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-27
Source: https://osv.dev/vulnerability/CVE-2022-4285
Type: osv

## Details
An illegal memory access flaw was found in the binutils package. Parsing an ELF file containing corrupt symbol version information may result in a denial of service. This issue is the result of an incomplete fix for CVE-2020-16599.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=5c831a3c7f3ca98d6aba1200353311e1a1f84c70
- https://security.gentoo.org/glsa/202309-15
- https://bugzilla.redhat.com/show_bug.cgi?id=2150768
- https://sourceware.org/bugzilla/show_bug.cgi?id=29699
