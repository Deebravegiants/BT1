# [C] CVE-2017-8305

## Summary
Severity: Critical
Advisory: CVE-2017-8305
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8305
Type: osv

## Details
The UDFclient (before 0.8.8) custom strlcpy implementation has a buffer overflow. UDFclient's strlcpy is used only on systems with a C library (e.g., glibc) that lacks its own strlcpy.

## References
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=861347
- http://www.13thmonkey.org/udfclient/
