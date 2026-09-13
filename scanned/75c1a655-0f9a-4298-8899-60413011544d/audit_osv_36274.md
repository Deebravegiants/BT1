# [M] Route Services Firewall Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-22726
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-22726
Type: osv

## Details
Route Services can be leveraged to send app traffic to network destinations outside of an app's configured egress rules. As a result, a malicious developer with access to Cloudfoundry could configure a route-service that would allow it to send requests to HTTP services on internal networks reachable by the Gorouter, which may not have previously had direct access from outside networks, or from the application.
Routing release: affected from v0.118.0 through v0.371.0 (inclusive); upgrade to v0.372.0 or greater. CF Deployment: affected from v0.0.2 through v54.14.0 (inclusive); upgrade to v55.0.0 or greater (includes routing_release v0.372.0).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22726.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22726
- https://www.cloudfoundry.org/blog/cve-2026-22726-route-services-firewall-bypass/
