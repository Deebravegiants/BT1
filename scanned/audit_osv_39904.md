# [C] Wazuh: cluster peer can read arbitrary master files and forge offline REST API administrator tokens via DAPI tmp_file path injection in Wazuh manager

## Summary
Severity: Critical
Advisory: CVE-2026-48162
Aliases: GHSA-r6f5-h662-8ffc
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-48162
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.0.0 until 4.14.6 and 5.0.0-beta3, DistributedAPI.send_tmp_file() in framework/wazuh/core/cluster/dapi/dapi.py joins an attacker-controlled tmp_file value to WAZUH_PATH without canonicalization or confinement. A cluster peer holding the shared Fernet key can use traversal or an absolute path to make the master return any readable file over the cluster channel. Reading /var/ossec/api/configuration/security/private_key.pem allows the peer to forge administrator REST API tokens offline and then exercise administrative privileges without creating an account. This issue is fixed in versions 4.14.6 and 5.0.0-beta3.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48162.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-r6f5-h662-8ffc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48162
- https://github.com/wazuh/wazuh/commit/de1eeedbe336744934be4e20d87d84a76e438cee
- https://github.com/wazuh/wazuh/pull/36246
