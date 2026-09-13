# [M] CVE-2015-8750

## Summary
Severity: Medium
Advisory: CVE-2015-8750
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2015-8750
Type: osv

## Details
libdwarf 20151114 and earlier allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a debug_abbrev section marked NOBITS in an ELF file.

## References
- http://www.openwall.com/lists/oss-security/2016/01/07/11
- https://bugzilla.redhat.com/show_bug.cgi?id=1294264
- https://github.com/tomhughes/libdwarf/commit/11750a2838e52953013e3114ef27b3c7b1780697
- http://www.openwall.com/lists/oss-security/2016/01/07/11
- http://www.openwall.com/lists/oss-security/2016/01/07/11
- https://github.com/tomhughes/libdwarf/commit/11750a2838e52953013e3114ef27b3c7b1780697
- https://bugzilla.redhat.com/show_bug.cgi?id=1294264
- https://github.com/tomhughes/libdwarf/commit/11750a2838e52953013e3114ef27b3c7b1780697
