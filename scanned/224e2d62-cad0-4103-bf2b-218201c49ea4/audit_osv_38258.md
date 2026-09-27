# [H] Pi-hole FTL affected by Remote Code Execution (RCE) via dhcp.leaseTime Newline Injection

## Summary
Severity: High
Advisory: CVE-2026-35520
Aliases: GHSA-fqv2-qhfh-ghcj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35520
Type: osv

## Details
FTLDNS (pihole-FTL) provides an interactive API and also generates statistics for Pi-hole's Web interface. From 6.0 to before 6.6, the Pi-hole FTL engine contains a Remote Code Execution (RCE) vulnerability in the DHCP lease time configuration parameter (dhcp.leaseTime). This vulnerability allows an authenticated attacker to inject arbitrary dnsmasq configuration directives through newline characters, ultimately achieving command execution on the underlying system. This vulnerability is fixed in 6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35520.json
- https://github.com/pi-hole/FTL/security/advisories/GHSA-fqv2-qhfh-ghcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35520
