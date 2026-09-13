# [C] Insecure Temporary File in SWHKD

## Summary
Severity: Critical
Advisory: GHSA-p4jg-pccf-h82c
CVE: CVE-2022-27815
CWE: CWE-377, CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-p4jg-pccf-h82c
Type: github-advisory

## Affected
- crates.io: `Simple-Wayland-HotKey-Daemon` — affected >=0 <1.2.0

## Details
SWHKD is a display protocol-independent hotkey daemon made in Rust. In SWHKD versions 1.1.5 and prior, SWHKD uses the /tmp/swhkd.pid pathname. As /tmp is accessible to all users, there can be an information leak or denial of service. No known workarounds exist. A patch is available on the `1.1.0` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27815
- https://github.com/waycrate/swhkd/commit/e661a4940df78fbb7b52c622ac4ae6a3a7f7d8aa
- https://github.com/waycrate/swhkd
- https://github.com/waycrate/swhkd/releases
- https://github.com/waycrate/swhkd/releases/tag/1.2.0
- http://www.openwall.com/lists/oss-security/2022/04/14/1
