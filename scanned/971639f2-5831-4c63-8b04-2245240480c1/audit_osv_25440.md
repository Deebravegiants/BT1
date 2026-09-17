# [M] CVE-2023-37008

## Summary
Severity: Medium
Advisory: CVE-2023-37008
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2023-37008
Type: osv

## Details
Open5GS MME versions <= 2.6.4 contain a buffer overflow in the ASN.1 deserialization function of the S1AP handler. This buffer overflow causes type confusion in decoded fields, leading to invalid parsing and freeing of memory. An attacker may use this to crash an MME or potentially execute code in certain circumstances.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37008.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37008
