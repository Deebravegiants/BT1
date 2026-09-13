# [H] Libinput: libinput: unauthorized code execution and information disclosure through lua bytecode plugins

## Summary
Severity: High
Advisory: CVE-2026-35093
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-35093
Type: osv

## Details
A flaw was found in libinput. A local attacker who can place a specially crafted Lua bytecode file in certain system or user configuration directories can bypass security restrictions. This allows the attacker to run unauthorized code with the same permissions as the program using libinput, such as a graphical compositor. This could lead to the attacker monitoring keyboard input and sending that information to an external location.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.freedesktop.org/libinput/libinput/-/work_items/1271
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-35093.json
- https://access.redhat.com/security/cve/CVE-2026-35093
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35093.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35093
- https://bugzilla.redhat.com/show_bug.cgi?id=2453839
