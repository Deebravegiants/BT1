# [M] Nmap 7.99 Denial of Service via Zero-Length TCP Option Packet

## Summary
Severity: Medium
Advisory: CVE-2026-72712
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72712
Type: osv

## Details
Nmap versions up to and including 7.99 contains a denial of service vulnerability that allows remote attackers to crash the application by sending a crafted packet containing a zero-length TCP option. The malformed packet forces the Packet:parse_options() function in nselib/packet.lua to allocate objects in an infinite loop, causing an out-of-memory condition that results in application crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72712.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72712
- https://www.vulncheck.com/advisories/nmap-denial-of-service-via-zero-length-tcp-option-packet
- https://github.com/nmap/nmap/issues/3368
- https://github.com/nmap/nmap/commit/7ef4ee030a0023fe22616387a000032e1a678b6a
- https://github.com/nmap/nmap
