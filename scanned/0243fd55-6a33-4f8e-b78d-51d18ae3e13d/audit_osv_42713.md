# [M] Dinky Unauthenticated System Configuration and Credential Disclosure via GET /api/sysConfig/getAll

## Summary
Severity: Medium
Advisory: CVE-2026-70559
Aliases: GHSA-c48m-x2xw-32rj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70559
Type: osv

## Details
Dinky's SysConfigController.getAll() handler for GET /api/sysConfig/getAll carries a method-level @SaIgnore annotation that short-circuits the class-level @SaCheckLogin, so the Sa-Token interceptor lets the request through with no session or role check. Any remote unauthenticated caller who can reach the Dinky HTTP port (8888 by default) receives the full live system configuration (54 entries on a stock v1.2.5 install) with one parameterless GET. Only one credential field (sys.maven.settings.repositoryPassword) has a desensitization handler wired; the other credential-bearing fields (sys.env.settings.dinkyToken, sys.ldap.settings.userPassword, sys.resource.settings.oss.accessKey and secretKey, and sys.dolphinscheduler.settings.token) return in cleartext. A bare install leaks the shipped defaults, including the hardcoded dinkyToken efda1551-7958-4e0f-80a8-dfd107df3e38 and minioadmin/minioadmin OSS keys; once an operator configures LDAP, object storage, or DolphinScheduler through the Settings Center, those live third-party credentials leak from the same endpoint. Because dinkyToken is the sole gate on the sibling POST /download/uploadFromRsByLocal arbitrary file write, this disclosure defeats token rotation as a mitigation for that vulnerability. Affects Dinky v1.2.5 (the current release, 2025-11-05) and the development branch (dev HEAD 63b5a5a), where the affected code is byte-identical.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70559.json
- https://github.com/DataLinkDC/dinky/security/advisories/GHSA-c48m-x2xw-32rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-70559
- https://github.com/DataLinkDC/dinky
- https://github.com/DataLinkDC/dinky/issues/4567
