# [C] Zigbee Green Power Host Buffer Overflow Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-8414
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2025-8414
Type: osv

## Details
Due to improper input validation, a buffer overflow vulnerability is present in 

Zigbee EZSP Host Applications. If the buffer overflows, stack corruption is possible. In certain

conditions, this could lead to arbitrary code execution. Access to a network key is required to exploit this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8414.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-8414
- https://community.silabs.com/068Vm00000WJZED
- https://github.com/SiliconLabs/gsdk
- https://github.com/SiliconLabs/simplicity_sdk
