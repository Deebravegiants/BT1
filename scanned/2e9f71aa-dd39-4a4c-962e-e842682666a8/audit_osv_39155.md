# [C] Wazuh Manager dapi RBAC Bypass Allows Privilege Escalation

## Summary
Severity: Critical
Advisory: CVE-2026-44252
Aliases: GHSA-34fx-c2xw-xcpg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-44252
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.0.0 until 4.14.5, Wazuh Manager allows a low-privilege read-only API user with manager:read permission to retrieve the cluster key from the element in ossec.conf through GET /manager/configuration?raw=true. An attacker with network access to TCP port 1516 can use the disclosed Fernet key to impersonate a cluster worker and submit distributed API requests containing attacker-controlled rbac_permissions with rbac_mode set to black. Because the master trusts the worker-supplied authorization context, the attacker can create users, assign administrator roles, access credentials and API tokens, modify configuration, and execute actions across agents. This issue is fixed in version 4.14.5.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.5
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44252.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-34fx-c2xw-xcpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44252
- https://github.com/wazuh/wazuh/commit/b3459f5663702aea14e91330a7a6912081fed2eb
- https://github.com/wazuh/wazuh/pull/35307
