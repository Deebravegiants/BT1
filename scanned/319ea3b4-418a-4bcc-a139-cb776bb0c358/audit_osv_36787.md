# [C] Wazuh Cluster vulnerable to Remote Code Execution via Insecure Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-25769
Aliases: GHSA-3gm7-962f-fxw5
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-25769
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. Versions 4.0.0 through 4.14.2 have a Remote Code Execution (RCE) vulnerability due to Deserialization of Untrusted Data). All Wazuh deployments using cluster mode (master/worker architecture) and any organization with a compromised worker node (e.g., through initial access, insider threat, or supply chain attack) are impacted. An attacker who gains access to a worker node (through any means) can achieve full RCE on the master node with root privileges. Version 4.14.3 fixes the issue.

## References
- https://drive.google.com/drive/folders/1WlkKNmHexz8212OVED9O6M_3pI8b6qNI?usp=sharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25769.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-3gm7-962f-fxw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25769
