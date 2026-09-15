# [M] Kanboard 1.2.52 and prior SSRF Filter Bypass via Hexadecimal IP Notation

## Summary
Severity: Medium
Advisory: CVE-2026-57862
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-57862
Type: osv

## Details
Kanboard 1.2.52 and prior contains a server-side request forgery vulnerability that allows authenticated users to bypass SSRF protections by supplying hexadecimal IP address notation in user-controlled URLs. Attackers can submit hexadecimal-encoded internal IP addresses through the web link creation feature, causing cURL to resolve and connect to internal network resources such as cloud instance metadata services, localhost services, and RFC1918 addresses while the isPrivateURL() filter in app/Core/Http/Client.php incorrectly treats the input as safe due to FILTER_VALIDATE_IP rejecting non-dotted-decimal notation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57862.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57862
- https://www.vulncheck.com/advisories/kanboard-and-prior-ssrf-filter-bypass-via-hexadecimal-ip-notation
- https://github.com/kanboard/kanboard
- https://gist.github.com/sermikr0/67c8acfc395e465127e729dc309da3ae
