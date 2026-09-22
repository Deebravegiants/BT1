# [C] Wazuh cluster sync path traversal in decompress_files() enables arbitrary file write and code execution from authenticated cluster peer

## Summary
Severity: Critical
Advisory: CVE-2026-30893
Aliases: GHSA-m8rw-v4f6-8787
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-30893
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From version 4.4.0 to before version 4.14.4, a path traversal vulnerability in Wazuh's cluster synchronization extraction routine allows an authenticated cluster peer to write arbitrary files outside the intended extraction directory on other cluster nodes. This can be escalated to code execution in the Wazuh service context by overwriting Python modules loaded by Wazuh components (proof of concept available as separate attachment). In deployments where the cluster daemon runs with elevated privileges, system-level compromise is possible. This issue has been patched in version 4.14.4.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30893.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-m8rw-v4f6-8787
- https://nvd.nist.gov/vuln/detail/CVE-2026-30893
