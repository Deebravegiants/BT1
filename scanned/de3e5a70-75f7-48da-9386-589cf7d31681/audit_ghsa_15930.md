# [M] Eclipse Jetty's ThreadLimitHandler.getRemote() vulnerable to remote DoS attacks

## Summary
Severity: Medium
Advisory: GHSA-g8m5-722r-8whq
CVE: CVE-2024-8184
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-g8m5-722r-8whq
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.0.0 <12.0.9
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.0 <10.0.24
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.0 <11.0.24
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.12 <9.4.56

## Details
### Impact
Remote DOS attack can cause out of memory 

### Description
There exists a security vulnerability in Jetty's `ThreadLimitHandler.getRemote()` which
can be exploited by unauthorized users to cause remote denial-of-service (DoS) attack.  By
repeatedly sending crafted requests, attackers can trigger OutofMemory errors and exhaust the
server's memory.

### Affected Versions

* Jetty 12.0.0-12.0.8 (Supported)
* Jetty 11.0.0-11.0.23 (EOL)
* Jetty 10.0.0-10.0.23 (EOL)
* Jetty 9.3.12-9.4.55 (EOL)

### Patched Versions

* Jetty 12.0.9
* Jetty 11.0.24
* Jetty 10.0.24
* Jetty 9.4.56

### Workarounds

Do not use `ThreadLimitHandler`.  
Consider use of `QoSHandler` instead to artificially limit resource utilization.

### References

Jetty 12 - https://github.com/jetty/jetty.project/pull/11723

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-g8m5-722r-8whq
- https://nvd.nist.gov/vuln/detail/CVE-2024-8184
- https://github.com/jetty/jetty.project/pull/11723
- https://github.com/jetty/jetty.project
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/30
- https://lists.debian.org/debian-lts-announce/2025/04/msg00001.html
