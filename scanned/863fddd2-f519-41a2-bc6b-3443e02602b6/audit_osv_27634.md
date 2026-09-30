# [H] CVE-2024-24420

## Summary
Severity: High
Advisory: CVE-2024-24420
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-24420
Type: osv

## Details
A reachable assertion in the decode_linked_ti_ie function of Magma <= 1.8.0 (fixed in v1.9 commit 08472ba98b8321f802e95f5622fa90fec2dea486) allows attackers to cause a Denial of Service (DoS) via a crafted NAS packet.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24420.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24420
