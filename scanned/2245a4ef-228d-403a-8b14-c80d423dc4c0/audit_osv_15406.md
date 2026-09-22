# [C] CVE-2019-15900

## Summary
Severity: Critical
Advisory: CVE-2019-15900
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-18
Source: https://osv.dev/vulnerability/CVE-2019-15900
Type: osv

## Details
An issue was discovered in slicer69 doas before 6.2 on certain platforms other than OpenBSD. On platforms without strtonum(3), sscanf was used without checking for error cases. Instead, the uninitialized variable errstr was checked and in some cases returned success even if sscanf failed. The result was that, instead of reporting that the supplied username or group name did not exist, it would execute the command as root.

## References
- https://github.com/slicer69/doas/compare/6.1p1...6.2
- https://github.com/slicer69/doas/commit/2f83222829448e5bc4c9391d607ec265a1e06531
