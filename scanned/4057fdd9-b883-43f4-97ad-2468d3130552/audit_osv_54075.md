# [C] CVE-2023-38336

## Summary
Severity: Critical
Advisory: CVE-2023-38336
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/CVE-2023-38336
Type: osv

## Details
netkit-rcp in rsh-client 0.17-24 allows command injection via filenames because /bin/sh is used by susystem, a related issue to CVE-2006-0225, CVE-2019-7283, and CVE-2020-15778.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1039689
