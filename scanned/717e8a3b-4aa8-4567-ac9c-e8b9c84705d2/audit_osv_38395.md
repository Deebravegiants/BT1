# [C] Pi-hole FTL remote code execution via newline injection in dns.interface configuration

## Summary
Severity: Critical
Advisory: CVE-2026-39849
Aliases: GHSA-9cqv-839p-gpq2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-39849
Type: osv

## Details
Pi-hole FTL is the core engine of the Pi-hole network-level advertisement and tracker blocker. In versions before 6.6.1, the `dns.interface` configuration field in Pi-hole FTL accepted newline characters without validation, allowing an attacker to inject arbitrary directives into the generated dnsmasq configuration file. On installations with no admin password set (the default for many deployments), the configuration API is fully accessible without credentials, allowing a network-adjacent attacker to inject the payload, enable the built-in DHCP server, and achieve arbitrary command execution on the host the next time any device on the network requests a DHCP lease. The injected value is persisted to /etc/pihole/pihole.toml and survives restarts. The strncpy in the code path limits the total interface field to 31 bytes, but payloads such as wlan0\ndhcp-script=/tmp/p fit within this constraint. The dnsmasq config validation introduced in FTL 6.6 only checks syntactic validity, so valid directives injected via newline pass validation successfully. This issue has been fixed in version 6.6.1.

## References
- https://github.com/pi-hole/FTL/releases/tag/v6.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39849.json
- https://github.com/pi-hole/FTL/security/advisories/GHSA-9cqv-839p-gpq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39849
- https://github.com/pi-hole/FTL/commit/0c46e4ec7fe57f762fce261625f2cf5d43806e6d
