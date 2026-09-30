# [M] Ability to view Agent list with no privilege access in wazuh-dashboard

## Summary
Severity: Medium
Advisory: CVE-2024-47770
Aliases: GHSA-648q-8m78-5cwv, GO-2025-3445
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2024-47770
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. It is capable of protecting workloads across on-premises, virtualized, containerized, and cloud-based environments. This vulnerability occurs when the system has weak privilege access, that allows an attacker to do privilege escalation. In this case the attacker is able to view agent list on Wazuh dashboard with no privilege access. This issue has been addressed in release version 4.9.1 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47770.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-648q-8m78-5cwv
- https://nvd.nist.gov/vuln/detail/CVE-2024-47770
