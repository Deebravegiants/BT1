# [C] arduino-TuyaOpen DnsServer Heap-Based Buffer Overflow Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-28519
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-15
Source: https://osv.dev/vulnerability/CVE-2026-28519
Type: osv

## Details
arduino-TuyaOpen before version 1.2.1 contains a heap-based buffer overflow vulnerability in the DnsServer component. An attacker on the same local area network who controls the LAN DNS server can send malicious DNS responses to overflow the heap buffer, potentially allowing execution of arbitrary code on affected embedded devices.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28519.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28519
- https://src.tuya.com/announcement/32
- https://www.vulncheck.com/advisories/arduino-tuyaopen-dnsserver-heap-based-buffer-overflow-remote-code-execution
- https://github.com/tuya/arduino-TuyaOpen
