# [H] Data Loss/Denial of Service in SWHKD

## Summary
Severity: High
Advisory: GHSA-8m49-2xj8-67v9
CVE: CVE-2022-27816
CWE: CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-8m49-2xj8-67v9
Type: github-advisory

## Affected
- crates.io: `Simple-Wayland-HotKey-Daemon` — affected >=0 <1.2.0

## Details
SWHKD 1.1.5 unsafely uses the /tmp/swhks.pid pathname. There can be data loss or a denial of service. A patch is available on the `1.1.0` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27816
- https://github.com/waycrate/swhkd/commit/0b620a09605afb815c6d8d8953bbb7a10a8c0575
- https://github.com/waycrate/swhkd
- https://github.com/waycrate/swhkd/releases/tag/1.2.0
- http://www.openwall.com/lists/oss-security/2022/04/14/1
