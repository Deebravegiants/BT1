# [C] Wazuh : peer-controlled metadata key in process_files_from_worker non-merged branch allows arbitrary file write under WAZUH_PATH on Wazuh manager

## Summary
Severity: Critical
Advisory: CVE-2026-49441
Aliases: GHSA-3v57-hgvj-3vj2
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-49441
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.3.0 until 4.14.6 and 5.0.0-beta3, the non-merged branch of process_files_from_worker() in framework/wazuh/core/cluster/master.py trusts a peer-controlled file_path key from files_metadata.json. The destination is joined to WAZUH_PATH without proving that it remains inside the directory selected by cluster_item_key. A cluster peer holding the shared Fernet key can upload a crafted extra-valid archive and overwrite security-sensitive files such as /var/ossec/etc/ossec.conf. Replacing ossec.conf can configure root-executed commands and lead to code execution after a service reload. This issue is fixed in versions 4.14.6 and 5.0.0-beta3.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49441.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-3v57-hgvj-3vj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49441
- https://github.com/wazuh/wazuh/commit/7f13682cf5f01f69452f723a608ab2d89cfb2133
- https://github.com/wazuh/wazuh/pull/36296
