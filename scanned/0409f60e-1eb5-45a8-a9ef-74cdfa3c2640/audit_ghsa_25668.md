# [M] Exposure of Resource to Wrong Sphere in Simple-Wayland-HotKey-Daemon

## Summary
Severity: Medium
Advisory: GHSA-h5wh-7h2j-h999
CVE: CVE-2022-27817
CWE: CWE-668
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2022-04-15
Source: https://github.com/advisories/GHSA-h5wh-7h2j-h999
Type: github-advisory

## Affected
- crates.io: `Simple-Wayland-HotKey-Daemon` — affected >=0

## Details
SWHKD 1.1.5 consumes the keyboard events of unintended users. This could potentially cause an information leak, but is usually a denial of functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27817
- https://github.com/waycrate/swhkd
- https://github.com/waycrate/swhkd/releases
- https://www.openwall.com/lists/oss-security/2022/04/14/1
