# [H] CVE-2026-48694

## Summary
Severity: High
Advisory: CVE-2026-48694
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48694
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains a configuration injection vulnerability in the Juniper router integration plugin. In src/juniper_plugin/fastnetmon_juniper.php, the $IP_ATTACK variable (received from argv[1]) is directly interpolated into Juniper NETCONF set-configuration commands at lines 69 and 90 without any validation or sanitization. Line 69: $conn->load_set_configuration("set routing-options static route {$IP_ATTACK} community 65535:666 discard"). Line 90: $conn->load_set_configuration("delete routing-options static route {$IP_ATTACK}/32"). An attacker who can control the IP address string can inject additional Juniper CLI configuration commands by embedding newline characters followed by arbitrary set/delete commands. This could modify the router's routing table, firewall filters, user accounts, or any other configuration element accessible via NETCONF. The impact is full router compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48694.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48694
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48694-juniper-netconf-injection
