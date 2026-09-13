# [M] CVE-2023-37010

## Summary
Severity: Medium
Advisory: CVE-2023-37010
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2023-37010
Type: osv

## Details
Open5GS MME versions <= 2.6.4 contain an assertion that can be remotely triggered via a malformed ASN.1 packet over the S1AP interface. An attacker may send an `eNB Status Transfer` message missing a required `MME_UE_S1AP_ID` field to repeatedly crash the MME, resulting in denial of service.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37010.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37010
