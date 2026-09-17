# [M] Wazuh: Local SQL injection in FIM db due to path lookup interpolation in wazuh-syscheckd

## Summary
Severity: Medium
Advisory: CVE-2026-49392
Aliases: GHSA-9c4x-mrjh-rmw5
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-49392
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.6.0 until 4.14.6 and 5.0.0-beta3, DB::getFile() and DB::searchFile() in src/syscheckd/src/db/src/file.cpp concatenate a monitored file path into SQLite row filters. On non-Windows systems, FIMDBCreator::encodeString() does not escape the value. A local user who can create a filename in a File Integrity Monitoring directory can inject a UNION SELECT expression when wazuh-syscheckd processes or deletes that path. The confirmed primitive manipulates SELECT result sets consumed by the FIM code; stacked statements and remote code execution were not demonstrated. This issue is fixed in versions 4.14.6 and 5.0.0-beta3.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49392.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-9c4x-mrjh-rmw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-49392
- https://github.com/wazuh/wazuh/commit/8e4e25b971dfb7b15bc492f10f8a350e6b37e70e
- https://github.com/wazuh/wazuh/pull/36399
