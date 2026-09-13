# [H] CVE-2023-37023

## Summary
Severity: High
Advisory: CVE-2023-37023
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2023-37023
Type: osv

## Details
Open5GS MME versions <= 2.6.4 contain a reachable assertion in the `Uplink NAS Transport` packet handler. A packet missing its `MME_UE_S1AP_ID` field causes Open5gs to crash; an attacker may repeatedly send such packets to cause denial of service.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37023.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37023
