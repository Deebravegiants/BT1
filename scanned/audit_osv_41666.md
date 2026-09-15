# [C] Axelor Open Platform 8.x < 8.2.2 Authorization Bypass via Nested Relational Record Persistence

## Summary
Severity: Critical
Advisory: CVE-2026-63085
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-63085
Type: osv

## Details
Axelor Open Platform versions 8.x prior to 8.2.2 contains an authorization bypass vulnerability that allows authenticated non-admin users to escalate privileges by exploiting unenforced field restrictions on nested relational save operations. Attackers can modify sensitive User record fields such as roles and group by submitting changes through a related entity's save path, bypassing the USER_RESTRICTED_FIELDS control and causing the JPA persistence layer to flush attacker-supplied admin role and group assignments on commit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63085.json
- https://github.com/axelor/axelor-open-platform/releases/tag/v8.2.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-63085
- https://www.vulncheck.com/advisories/axelor-open-platform-8-x-authorization-bypass-via-nested-relational-record-persistence
- https://github.com/axelor/axelor-open-platform
- https://github.com/geo-chen/oss/blob/main/axelor-open-platform.md
