# [M] Server-Side Request Forgery protection bypass in misp-modules html_to_markdown via IPv4-mapped IPv6 addresses

## Summary
Severity: Medium
Advisory: CVE-2026-62143
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/AU:Y/RE:M/U:Green)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62143
Type: osv

## Details
A Server-Side Request Forgery (SSRF) protection bypass existed in the html_to_markdown expansion module of misp-modules.

The module attempts to prevent requests to loopback, private, link-local, and other restricted IP address ranges. However, IP addresses were compared against the blocked ranges without first normalising IPv4-mapped IPv6 addresses.

An authenticated attacker able to invoke the module could supply an IPv4-mapped IPv6 address, such as:

http://[::ffff:127.0.0.1]/
http://[::ffff:169.254.169.254]/

Alternatively, the attacker could use a hostname that resolves to an IPv4-mapped IPv6 address. These addresses were treated as IPv6 addresses and therefore did not match the corresponding blocked IPv4 ranges.

Successful exploitation could cause the misp-modules server to connect to services available through its loopback interface, internal network, or link-local network. This could expose internal web services, administrative interfaces, or cloud instance metadata, with retrieved content potentially returned to the attacker as converted Markdown.

The vulnerability has been addressed by normalising IPv4-mapped IPv6 addresses to their underlying IPv4 representation before applying the blocked-range checks. URLs without a valid hostname are now also rejected.

## References
- https://github.com/MISP/misp-modules/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62143.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62143
- https://github.com/MISP/misp-modules/commit/3bae4108a3ba1e507727d5264697fd7303ba0b89
