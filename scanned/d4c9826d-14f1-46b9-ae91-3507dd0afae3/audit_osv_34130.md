# [M] CVE-2025-55102

## Summary
Severity: Medium
Advisory: CVE-2025-55102
Aliases: GHSA-f3rx-xrwm-q2rf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-55102
Type: osv

## Details
A denial-of-service vulnerability exists in the NetX IPv6 component functionality of Eclipse ThreadX NetX Duo. A specially crafted network packet of "Packet Too Big" with more than 15 different source address can lead to denial of service. An attacker can send a malicious packet to trigger this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55102.json
- https://github.com/eclipse-threadx/netxduo/security/advisories/GHSA-f3rx-xrwm-q2rf
- https://nvd.nist.gov/vuln/detail/CVE-2025-55102
- https://github.com/eclipse-threadx/netxduo
