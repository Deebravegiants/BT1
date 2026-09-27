# [M] Unsafe parsing in SWHKD

## Summary
Severity: Medium
Advisory: GHSA-h6xw-mghq-7523
CVE: CVE-2022-27819
CWE: CWE-400, CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-h6xw-mghq-7523
Type: github-advisory

## Affected
- crates.io: `Simple-Wayland-HotKey-Daemon` — affected >=0 <1.2.0

## Details
SWHKD 1.1.5 allows unsafe parsing via the -c option. An information leak might occur but there is a simple denial of service (memory exhaustion) upon an attempt to parse a large or infinite file (such as a block or character device).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27819
- https://github.com/waycrate/swhkd/commit/b4e6dc76f4845ab03104187a42ac6d1bbc1e0021
- https://github.com/waycrate/swhkd
- https://github.com/waycrate/swhkd/releases
- https://github.com/waycrate/swhkd/releases/tag/1.2.0
- http://www.openwall.com/lists/oss-security/2022/04/14/1
