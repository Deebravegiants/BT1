# [M] vlife-base has Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cg6m-9276-qpjj
CVE: CVE-2025-13266
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-cg6m-9276-qpjj
Type: github-advisory

## Affected
- Maven: `io.github.wwwlike:vlife-base` — affected >=0

## Details
A security vulnerability has been detected in wwwlike vlife up to 2.0.1. This issue affects the function create of the file vlife-base/src/main/java/cn/wwwlike/sys/api/SysFileApi.java of the component VLifeApi. Such manipulation of the argument fileName leads to path traversal. It is possible to launch the attack remotely. The exploit has been disclosed publicly and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13266
- https://github.com/wwwlike/vlife/issues/3
- https://github.com/wwwlike/vlife
- https://vuldb.com/?ctiid.332601
- https://vuldb.com/?id.332601
- https://vuldb.com/?submit.689436
