# [M] DoS Vulnerability in ntpd-rs

## Summary
Severity: Medium
Advisory: GHSA-4855-q42w-5vr4
CVE: CVE-2025-58066
CWE: CWE-406
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-4855-q42w-5vr4
Type: github-advisory

## Affected
- crates.io: `ntpd-rs` — affected >=1.2.0 <1.6.2

## Details
# Summary

A denial of service vulnerability was discovered in ntpd-rs where an attacker can induce a message storm between two NTP servers running ntpd-rs.

# Details

Since ntpd-rs version 1.2.0, when configured as a server, incorrectly responded to all NTP messages sent to the server's port with a time reply, including to responses from other servers. As a consequence, a message with a spoofed IP address of another server could cause two servers running ntpd-rs to continually respond to each other, consuming significant amounts of resources.

# Impact

Any time server running ntpd-rs with version between 1.2.0 and 1.6.1 inclusive which allows non-NTS traffic is affected. Client-only configurations are not affected. Affected users are recommended to upgrade to version 1.6.2 as soon as possible.

# Workarounds

Should upgrading not be possible, the impact of the issue can be mitigated by:
 - Whitelisting access to only IP addresses of clients using the server, using the ignore filter method.
 - Blocking incoming non-request traffic on the NTP server port using a firewall.
 - Disabling public access to the vulnerable NTP server
 - Disabling the server functionality by removing any [server] sections from the configuration.

# Acknowledgements

The ntpd-rs authors thank Eric Sesterhenn from X41 D-Sec GmbH for finding and reporting this issue.

## References
- https://github.com/pendulum-project/ntpd-rs/security/advisories/GHSA-4855-q42w-5vr4
- https://nvd.nist.gov/vuln/detail/CVE-2025-58066
- https://github.com/pendulum-project/ntpd-rs/commit/da37cf167736cbd4d7804b1ed7ceb572468298e0
- https://github.com/pendulum-project/ntpd-rs
