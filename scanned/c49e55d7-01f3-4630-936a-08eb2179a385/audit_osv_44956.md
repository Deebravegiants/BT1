# [M] Net-SNMP through 5.9.5.2 Denial of Service via Blocking Unauthenticated SMUX Read

## Summary
Severity: Medium
Advisory: CVE-2026-89147
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-89147
Type: osv

## Details
Net-SNMP through 5.9.5.2 contains a denial of service vulnerability in the SMUX module where smux_accept() performs an unauthenticated blocking read without timeout on newly accepted connections. An unauthenticated remote client can connect to the SMUX listener and send no data, causing the single-threaded snmpd main loop to block indefinitely and suspend all SNMP processing.

## References
- https://gist.github.com/thesmartshadow/001cea595e75fed6aaea7389666dc9eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89147.json
- https://github.com/net-snmp/net-snmp
- https://github.com/net-snmp/net-snmp/blob/v5.9.5.2/agent/mibgroup/smux/smux.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-89147
- https://www.vulncheck.com/advisories/net-snmp-through-5.9.5.2-denial-of-service-via-blocking-unauthenticated-smux-read
