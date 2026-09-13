# [M] Heap buffer overflow in wazuh-analysisd

## Summary
Severity: Medium
Advisory: CVE-2025-59938
Aliases: GHSA-vw3r-mjg3-9hh2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-27
Source: https://osv.dev/vulnerability/CVE-2025-59938
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. In versions starting from 3.8.0 to before 4.11.0, wazuh-analysisd is vulnerable to a heap buffer overflow when parsing XML elements from Windows EventChannel messages. This issue has been patched in version 4.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59938.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-vw3r-mjg3-9hh2
- https://nvd.nist.gov/vuln/detail/CVE-2025-59938
