# [M] Packetbeat Out-of-bounds Read

## Summary
Severity: Medium
Advisory: CVE-2025-68382
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-68382
Type: osv

## Details
Out-of-bounds read (CWE-125) allows an unauthenticated remote attacker to perform a buffer overflow (CAPEC-100) via the NFS protocol dissector, leading to a denial-of-service (DoS) through a reliable process crash when handling truncated XDR-encoded RPC messages.

## References
- https://discuss.elastic.co/t/packetbeat-8-19-9-9-1-9-and-9-2-3-security-update-esa-2025-31/384179
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68382.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68382
