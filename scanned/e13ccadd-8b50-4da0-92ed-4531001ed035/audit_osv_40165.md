# [H] CVE-2026-50292

## Summary
Severity: High
Advisory: CVE-2026-50292
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-50292
Type: osv

## Details
In libinput before 1.30.4 and 1.31.x before 1.31.3, libinput-device-group unescaped phys output can inject udev properties leading to arbitrary root code execution

## References
- https://gitlab.freedesktop.org/libinput/libinput/-/work_items/1296
- https://www.openwall.com/lists/oss-security/2026/06/04/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50292.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50292
- https://gitlab.freedesktop.org/libinput/libinput/-/commit/76f0d8a7f57e2868882864b4611281f12f704b55
