# [C] NebulaGraph through 3.8.0 Unauthenticated Read and Modification of Runtime Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-81032
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-81032
Type: osv

## Details
NebulaGraph exposes its runtime configuration over an unauthenticated HTTP service. Each daemon starts the web service defined in src/webservice/WebService.cpp, whose bind address defaults to all interfaces, and registers routes for reading and writing gflags alongside status and statistics. Neither the service nor its router carries any authentication, token check or address restriction. The read route returns the daemon's full set of runtime flag values, which includes the configured certificate, key and certificate-authority paths, the password file path, data directories and the transport-security enable flags. The write route parses a supplied map and applies each entry through the gflags runtime setter, so a caller able to reach the port can change the daemon's behaviour without restarting it, including disabling the transport-security flags, redirecting log files and altering flags such as failed_login_attempts and password_lock_time_in_secs. Public reports of this endpoint describe a single name, enable_authorize, being refused by the handler; at release 3.8.0 that refusal is not present and the handler applies every name it is given.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81032.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81032
- https://www.vulncheck.com/advisories/nebulagraph-through-3.8.0-unauthenticated-read-and-modification-of-runtime-configuration
- https://github.com/vesoft-inc/nebula/issues/6157
- https://github.com/vesoft-inc/nebula
- https://github.com/vesoft-inc/nebula/blob/v3.8.0/src/webservice/SetFlagsHandler.cpp
- https://github.com/vesoft-inc/nebula/blob/v3.8.0/src/webservice/WebService.cpp
