# [H] CVE-2025-65562

## Summary
Severity: High
Advisory: CVE-2025-65562
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-65562
Type: osv

## Details
The free5GC UPF suffers from a lack of bounds checking on the SEID when processing PFCP Session Deletion Requests. An unauthenticated remote attacker can send a request with a very large SEID (e.g., 0xFFFFFFFFFFFFFFFF) that causes an integer conversion/underflow in LocalNode.DeleteSess() / LocalNode.Sess() when a uint64 SEID is converted to int and used in index arithmetic. This leads to a negative index into n.sess and a Go runtime panic, resulting in a denial of service (UPF crash). The issue has been reproduced on free5GC v4.1.0 with crashes observed in the session lookup/deletion path in internal/pfcp/node.go; other versions may also be affected. No authentication is required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65562.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65562
- https://github.com/free5gc/free5gc/issues/731
