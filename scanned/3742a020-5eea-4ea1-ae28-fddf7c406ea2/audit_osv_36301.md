# [C] FreeRDP has a heap-use-after-free in create_irp_thread

## Summary
Severity: Critical
Advisory: CVE-2026-22856
Aliases: GHSA-w842-c386-fxhv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22856
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, a race in the serial channel IRP thread tracking allows a heap use‑after‑free when one thread removes an entry from serial->IrpThreads while another reads it. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22856.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-w842-c386-fxhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-22856
