# [M] CVE-2017-9778

## Summary
Severity: Medium
Advisory: CVE-2017-9778
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-21
Source: https://osv.dev/vulnerability/CVE-2017-9778
Type: osv

## Details
GNU Debugger (GDB) 8.0 and earlier fails to detect a negative length field in a DWARF section. A malformed section in an ELF binary or a core file can cause GDB to repeatedly allocate memory until a process limit is reached. This can, for example, impede efforts to analyze malware with GDB.

## References
- http://www.securityfocus.com/bid/99244
- https://sourceware.org/bugzilla/show_bug.cgi?id=21600
