# [H] CVE-2026-85199

## Summary
Severity: High
Advisory: CVE-2026-85199
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85199
Type: osv

## Details
Eclipse aeriOS Self-orchestrator versions prior to 1.2.1 contain a path traversal vulnerability in the REST API. User-controlled identifiers used to create, update, or delete Self-orchestrator resources were incorporated into filesystem paths without adequate validation or sanitization. An unauthenticated remote attacker able to access the Self-orchestrator API could therefore supply specially crafted identifiers containing path traversal sequences to write or delete JSON files outside the intended application directories, subject to the filesystem permissions of the Self-orchestrator process.




The impact is increased by the absence of authentication on the affected API and by the container running with elevated privileges in the affected deployment configuration.




The issue has been addressed in version 1.2.1 by introducing validation and sanitization of user-controlled identifiers before they are used to construct filesystem paths, preventing path separator characters from being used to escape the intended directories.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/832
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85199
- https://github.com/eclipse-aerios/self-orchestrator/commit/c42da0014069528d149ff9f8b038ac93c38a766c
