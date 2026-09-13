# [C] CVE-2024-24421

## Summary
Severity: Critical
Advisory: CVE-2024-24421
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-24421
Type: osv

## Details
A type confusion in the nas_message_decode function of Magma <= 1.8.0 (fixed in v1.9 commit 08472ba98b8321f802e95f5622fa90fec2dea486) allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via a crafted NAS packet.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24421.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24421
