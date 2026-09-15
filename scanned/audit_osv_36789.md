# [C] Wazuh has Privilege Escalation to Root via Cluster Protocol File Write

## Summary
Severity: Critical
Advisory: CVE-2026-25770
Aliases: GHSA-r4f7-v3p6-79jm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-25770
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. Starting in version 3.9.0 and prior to version 4.14.3, a privilege escalation vulnerability exists in the Wazuh Manager's cluster synchronization protocol. The `wazuh-clusterd` service allows authenticated nodes to write arbitrary files to the manager’s file system with the permissions of the `wazuh` system user. Due to insecure default permissions, the `wazuh` user has write access to the manager's main configuration file (`/var/ossec/etc/ossec.conf`). By leveraging the cluster protocol to overwrite `ossec.conf`, an attacker can inject a malicious `<localfile>` command block. The `wazuh-logcollector` service, which runs as root, parses this configuration and executes the injected command. This chain allows an attacker with cluster credentials to gain full Root Remote Code Execution, violating the principle of least privilege and bypassing the intended security model. Version 4.14.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25770.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-r4f7-v3p6-79jm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25770
