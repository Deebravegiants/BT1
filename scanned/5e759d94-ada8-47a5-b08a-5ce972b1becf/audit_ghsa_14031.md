# [H] Improper handling of NTS cookie length that could crash the ntpd-rs server

## Summary
Severity: High
Advisory: GHSA-qwhm-h7v3-mrjx
CVE: CVE-2023-33192
CWE: CWE-130
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-25
Source: https://github.com/advisories/GHSA-qwhm-h7v3-mrjx
Type: github-advisory

## Affected
- crates.io: `ntpd` — affected >=0.3.0 <0.3.3

## Details
### Impact
ntpd-rs does not validate the length of NTS cookies in received NTP packets to the server. An attacker can crash the server by sending a specially crafted NTP packet containing a cookie shorter than what the server expects. The server also crashes when it is not configured to handle NTS packets.

ntpd-rs running purely as an ntp client is not affected.

### Patches
The issue was caused by improper slice indexing. The indexing operations were replaced by safer alternatives that do not crash the ntpd-rs server process but instead properly handle the error condition. A patch was released in version 0.3.3

### Workarounds
ntpd-rs running purely as an ntp client is not affected. By default, ntpd-rs packages are not configured to run as a server.

For machines where serving the time is required, there is no known workaround. Users are recommended to upgrade ntpd-rs as soon as possible.

### References
https://github.com/pendulum-project/ntpd-rs/pull/752

We would like to thank @mlichvar for identifying this issue

## References
- https://github.com/pendulum-project/ntpd-rs/security/advisories/GHSA-qwhm-h7v3-mrjx
- https://nvd.nist.gov/vuln/detail/CVE-2023-33192
- https://github.com/pendulum-project/ntpd-rs/pull/752
- https://github.com/pendulum-project/ntpd-rs
- https://github.com/pendulum-project/ntpd-rs/releases/tag/v0.3.3
