# [M] CVE-2025-66910

## Summary
Severity: Medium
Advisory: CVE-2025-66910
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-66910
Type: osv

## Details
Turms Server v0.10.0-SNAPSHOT and earlier contains a plaintext password storage vulnerability in the administrator authentication system. The BaseAdminService class caches administrator passwords in plaintext within AdminInfo objects to optimize authentication performance. Upon successful login, raw passwords are stored unencrypted in memory in the rawPassword field. Attackers with local system access can extract these passwords through memory dumps, heap analysis, or debugger attachment, bypassing bcrypt protection.

## References
- https://github.com/Xzzz111/public_cve_report/blob/main/CVE-2025-66910_report.md
- https://github.com/turms-im/turms/blob/develop/turms-server-common/src/main/java/im/turms/server/common/domain/admin/bo/AdminInfo.java#L34
- https://github.com/turms-im/turms/blob/develop/turms-server-common/src/main/java/im/turms/server/common/domain/admin/service/BaseAdminService.java#L237
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66910.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66910
- https://github.com/turms-im/turms
