# [H] Eclipse Jetty: DoS attack triggering OutOfMemory with 100-Continue requests

## Summary
Severity: High
Advisory: GHSA-9299-c6m4-mjhc
CVE: CVE-2024-7708
CWE: CWE-400, CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-9299-c6m4-mjhc
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.7 <10.0.23
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.7 <11.0.23

## Details
### Impact
The original report:

> Server handling of 100-Continue requests can lead to memory leak that can be abused to cause a Denial of Service state.

After investigation, turns out that every request that has a body, but reading the body may end up in reading 0 bytes, leaks a buffer.
This is particularly the case for 100-Continue, but any request where the network is slow can leak.

### Affected Versions

* Jetty 11.0.0-11.0.22 (EOL)
* Jetty 10.0.0-10.0.22 (EOL)

### Patched Versions

* Jetty 11.0.23
* Jetty 10.0.23

### Patches

https://github.com/jetty/jetty.project/pull/12156

### Workarounds

No workarounds.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-9299-c6m4-mjhc
- https://nvd.nist.gov/vuln/detail/CVE-2024-7708
- https://github.com/jetty/jetty.project/pull/12156
- https://github.com/jetty/jetty.project/commit/8259eabbc70ae7fc2d525f1e95b43fbdfd2ad097
- https://github.com/jetty/jetty.project
- https://github.com/jetty/jetty.project/releases/tag/jetty-10.0.23
- https://github.com/jetty/jetty.project/releases/tag/jetty-11.0.23
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/29
