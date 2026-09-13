# [H] Eclipse Jetty HTTP/2 client can force the server to allocate a humongous byte buffer that may lead to OoM and subsequently the JVM to exit

## Summary
Severity: High
Advisory: GHSA-889j-63jv-qhr8
CVE: CVE-2025-1948
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-08
Source: https://github.com/advisories/GHSA-889j-63jv-qhr8
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.http2:jetty-http2-common` — affected >=12.0.0 <12.0.17

## Details
### Original Report

In Eclipse Jetty versions 12.0.0 to 12.0.16 included, an HTTP/2 client can specify a very large value for the HTTP/2 settings parameter SETTINGS_MAX_HEADER_LIST_SIZE. The Jetty HTTP/2 server does not perform validation on this setting, and tries to allocate a ByteBuffer of the specified capacity to encode HTTP responses, likely resulting in OutOfMemoryError being thrown, or even the JVM process exiting.

### Impact
Remote peers can cause the JVM to crash or continuously report OOM.

### Patches
12.0.17

### Workarounds
No workarounds.

### References
https://github.com/jetty/jetty.project/issues/12690

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-889j-63jv-qhr8
- https://nvd.nist.gov/vuln/detail/CVE-2025-1948
- https://github.com/jetty/jetty.project/issues/12690
- https://github.com/jetty/jetty.project/commit/c8c2515936ef968dc8a3cecd9e79d1e69291e4bb
- https://github.com/jetty/jetty.project
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/56
