# [M] CVE-2017-17080

## Summary
Severity: Medium
Advisory: CVE-2017-17080
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-30
Source: https://osv.dev/vulnerability/CVE-2017-17080
Type: osv

## Details
elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, does not validate sizes of core notes, which allows remote attackers to cause a denial of service (bfd_getl32 heap-based buffer over-read and application crash) via a crafted object file, related to elfcore_grok_netbsd_procinfo, elfcore_grok_openbsd_procinfo, and elfcore_grok_nto_status.

## References
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22421
