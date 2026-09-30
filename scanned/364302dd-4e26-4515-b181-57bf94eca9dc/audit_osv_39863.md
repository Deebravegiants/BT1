# [C] Wazuh: merged-file header path traversal in cluster sync allows arbitrary file write under WAZUH_PATH in Wazuh manager

## Summary
Severity: Critical
Advisory: CVE-2026-48024
Aliases: GHSA-gh4h-fx78-q8xc
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-48024
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.0.0 until 4.14.6 and 5.0.0-beta3, cluster.unmerge_info() in framework/wazuh/core/cluster/cluster.py constructs paths from peer-controlled merge_type and name values in a merged synchronization archive. process_files_from_worker() in framework/wazuh/core/cluster/master.py does not adequately confine the resulting path to the declared cluster item directory. A cluster peer holding the shared Fernet key can use traversal in files_metadata.json or a merged-file header to write files such as /var/ossec/etc/ossec.conf. Replacing ossec.conf can configure root-executed commands and lead to code execution when Wazuh services reload. This issue is fixed in versions 4.14.6 and 5.0.0-beta3.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48024.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-gh4h-fx78-q8xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48024
- https://github.com/wazuh/wazuh/commit/88fc89fdfb1bf37b9d826e9c281a3d22655733de
- https://github.com/wazuh/wazuh/pull/36204
