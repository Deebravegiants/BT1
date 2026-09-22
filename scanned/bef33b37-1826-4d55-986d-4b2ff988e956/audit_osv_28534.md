# [H] CVE-2024-34235

## Summary
Severity: High
Advisory: CVE-2024-34235
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2024-34235
Type: osv

## Details
Open5GS MME versions <= 2.6.4 contains an assertion that can be remotely triggered via a malformed ASN.1 packet over the S1AP interface. An attacker may send an `Initial UE Message` missing a required `NAS_PDU` field to repeatedly crash the MME, resulting in denial of service.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34235.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34235
