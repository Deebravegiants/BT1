# [H] Unlimited number of NTS-KE connections can crash ntpd-rs server

## Summary
Severity: High
Advisory: GHSA-2xpx-vcmq-5f72
CVE: CVE-2024-38528
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-28
Source: https://github.com/advisories/GHSA-2xpx-vcmq-5f72
Type: github-advisory

## Affected
- crates.io: `ntpd` — affected >=0.3.1 <1.1.3

## Details
### Summary
Missing limit for accepted NTS-KE connections allows an unauthenticated remote attacker to crash ntpd-rs when an NTS-KE server is configured. Non NTS-KE server configurations, such as the default ntpd-rs configuration, are unaffected.

### Details
Operating systems have a limit for the number of open file descriptors (which includes sockets) in a single process, e.g. 1024 on Linux by default. When ntpd-rs is configured as an NTS server, it accepts TCP connections for the NTS-KE service. If the process has reached the descriptor limit and tries to accept a new TCP connection, the accept() system call will return with the EMFILE error and cause ntpd-rs to abort.

A remote attacker can open a large number of parallel TCP connections to the server to trigger this crash. The connections need to be opened quickly enough to avoid the `key-exchange-timeout-ms` timeout (by default 1000 milliseconds).

### Impact
Only NTS-KE server configuration are affected. Those without an NTS-KE server configuration such as NTS client only or NTP only configuration are unaffected. For affected configurations the ntpd-rs daemon can made completely unavailable by crashing the service. If ntpd-rs is automatically restarted, an attacker can repeat the attack to prevent ntpd-rs from doing anything useful.

### Workarounds
- Disable NTS-KE server functionality
- Increase system resource limits (`RLIMIT_NOFILE`) to make the attack more difficult
- Lower the `key-exchange-timeout-ms` configuration setting to make the attack more difficult

## References
- https://github.com/pendulum-project/ntpd-rs/security/advisories/GHSA-2xpx-vcmq-5f72
- https://nvd.nist.gov/vuln/detail/CVE-2024-38528
- https://github.com/pendulum-project/ntpd-rs/commit/6049687006ea5b26eeac927964b5fcc80d7bde50
- https://github.com/pendulum-project/ntpd-rs
