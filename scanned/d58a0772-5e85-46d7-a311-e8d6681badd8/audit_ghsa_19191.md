# [M] ntpd NTS client denial of service via wrongly sized cookies

## Summary
Severity: Medium
Advisory: GHSA-v83q-83hj-rw38
CWE: CWE-369, CWE-703
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-28
Source: https://github.com/advisories/GHSA-v83q-83hj-rw38
Type: github-advisory

## Affected
- crates.io: `ntpd` — affected >=0 <1.5.0

## Details
Two denial of service vulnerabilities were found in ntpd-rs related to the handling of NTS cookies in our client functionality. Whenever an NTS source is configured and the server behind that source is sending zero-sized cookies or cookies larger than what would fit in our buffer size, ntpd-rs would crash. Only configured NTS sources can abuse these vulnerabilities. NTP sources or third parties that are not configured cannot make use of these vulnerabilities.

For zero-sized cookies: a division by zero would force an exit when the number of new cookies that would need to be requested is calculated. In ntpd-rs 1.5.0 a check was added to prevent the division by zero.

For large cookies: while trying to send a NTP request with the cookie included, the buffer is too small to handle the cookie and an exit of ntpd-rs is forced once a write to the buffer is attempted. The memory outside the buffer would not be written to in this case. In ntpd-rs 1.5.0 a check was added that prevents accepting cookies larger than 350 bytes.

Users of older versions of ntpd-rs are recommended to update to the latest version. If an update is impossible, it is recommended to only add NTS sources to ntpd-rs that are trusted to not abuse this bug.

## References
- https://github.com/pendulum-project/ntpd-rs/security/advisories/GHSA-v83q-83hj-rw38
- https://github.com/pendulum-project/ntpd-rs/commit/10a103b471dae25ac598140df0c195b6531bf716
- https://github.com/pendulum-project/ntpd-rs/commit/37dd8d9a0faa03e7dfe3a4bf64953010f075c3e2
- https://github.com/pendulum-project/ntpd-rs
