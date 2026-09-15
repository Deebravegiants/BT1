# [M] Packetbeat Improper Bounds Check

## Summary
Severity: Medium
Advisory: CVE-2025-68381
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-68381
Type: osv

## Details
Improper Bounds Check (CWE-787) in Packetbeat can allow a remote unauthenticated attacker to exploit a Buffer Overflow (CAPEC-100) and reliably crash the application or cause significant resource exhaustion via a single crafted UDP packet with an invalid fragment sequence number.

## References
- https://discuss.elastic.co/t/packetbeat-8-19-9-9-1-9-and-9-2-3-security-update-esa-2025-30/384178
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68381.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68381
