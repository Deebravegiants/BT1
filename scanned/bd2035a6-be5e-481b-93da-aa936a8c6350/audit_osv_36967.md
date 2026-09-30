# [M] HomeBox affected by Blind SSRF

## Summary
Severity: Medium
Advisory: CVE-2026-27600
Aliases: GHSA-cm7p-5mg5-82pm
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-27600
Type: osv

## Details
HomeBox is a home inventory and organization system. Prior to 0.24.0-rc.1, the notifier functionality allows authenticated users to specify arbitrary URLs to which the application sends HTTP POST requests. No validation or restriction is applied to the supplied host, IP address, or port. Although the application does not return the response body from the target service, its UI behavior differs depending on the network state of the destination. This creates a behavioral side-channel that enables internal service enumeration. This vulnerability is fixed in 0.24.0-rc.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27600.json
- https://github.com/sysadminsmedia/homebox/security/advisories/GHSA-cm7p-5mg5-82pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-27600
