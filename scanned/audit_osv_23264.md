# [M] CVE-2022-46338

## Summary
Severity: Medium
Advisory: CVE-2022-46338
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-11-30
Source: https://osv.dev/vulnerability/CVE-2022-46338
Type: osv

## Details
g810-led 0.4.2, a LED configuration tool for Logitech Gx10 keyboards, contained a udev rule to make supported device nodes world-readable and writable, allowing any process on the system to read traffic from keyboards, including sensitive data.

## References
- https://bugs.debian.org/1024998
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46338.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46338
- https://github.com/MatMoul/g810-led/pull/297
- https://lists.debian.org/debian-lts-announce/2022/12/msg00002.html
