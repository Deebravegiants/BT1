# [C] Wazuh Analysis Engine Event Decoder Heap-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-32038
Aliases: GHSA-fcpw-v3pg-c327
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2024-32038
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. There is a buffer overflow hazard in wazuh-analysisd when handling Unicode characters from Windows Eventchannel messages. It impacts Wazuh Manager 3.8.0 and above. This vulnerability is fixed in Wazuh Manager 4.7.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32038.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-fcpw-v3pg-c327
- https://nvd.nist.gov/vuln/detail/CVE-2024-32038
