# [M] StarRocks Frontend REST Handlers Bypass the Base Class Authentication Gate

## Summary
Severity: Medium
Advisory: CVE-2026-82276
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82276
Type: osv

## Details
StarRocks through 4.0.13 contains an authentication bypass vulnerability in five REST handler classes that override execute() directly instead of implementing executeWithoutPassword(). Attackers can access six unauthenticated endpoints on the frontend HTTP port to disclose cluster topology, database metadata, JVM statistics, and version information without credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82276.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82276
- https://www.vulncheck.com/advisories/starrocks-frontend-rest-handlers-bypass-the-base-class-authentication-gate
- https://github.com/StarRocks/starrocks/issues/75747
- https://github.com/StarRocks/starrocks
- https://github.com/StarRocks/starrocks/blob/4.0.13/fe/fe-core/src/main/java/com/starrocks/http/rest/RestBaseAction.java
- https://github.com/StarRocks/starrocks/blob/4.0.13/fe/fe-core/src/main/java/com/starrocks/http/rest/ShowMetaInfoAction.java
