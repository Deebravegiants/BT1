# [M] CVE-2023-37030

## Summary
Severity: Medium
Advisory: CVE-2023-37030
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2023-37030
Type: osv

## Details
A Null pointer dereference vulnerability in the Mobile Management Entity (MME) in Magma <= 1.8.0 (fixed in v1.9 commit 08472ba98b8321f802e95f5622fa90fec2dea486) allows network-adjacent attackers to crash the MME via an S1AP `Initial UE Message` packet missing an expected `eNB_UE_S1AP_ID` field.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37030.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37030
