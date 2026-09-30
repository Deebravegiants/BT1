# [C] CVE-2024-31570

## Summary
Severity: Critical
Advisory: CVE-2024-31570
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-19
Source: https://osv.dev/vulnerability/CVE-2024-31570
Type: osv

## Details
libfreeimage in FreeImage 3.4.0 through 3.18.0 has a stack-based buffer overflow in the PluginXPM.cpp Load function via an XPM file.

## References
- https://www.openwall.com/lists/oss-security/2024/04/11/10
- https://sourceforge.net/p/freeimage/bugs/355/
