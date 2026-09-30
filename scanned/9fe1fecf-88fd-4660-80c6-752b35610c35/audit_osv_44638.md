# [M] Kill Bill through 0.24.21 Missing Authorization on AdminResource Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-85213
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85213
Type: osv

## Details
Kill Bill through 0.24.21 fails to enforce permission annotations on several AdminResource endpoints including getQueueEntries, invalidatesCache, and putOutOfRotation. Authenticated users with minimal account:read permissions can read internal queues, flush server caches, and disable the server by putting the host out of rotation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85213.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85213
- https://www.vulncheck.com/advisories/kill-bill-through-0.24.21-missing-authorization-on-adminresource-endpoints
- https://github.com/killbill/killbill/issues/2251
- https://github.com/killbill/killbill
- https://github.com/killbill/killbill/blob/killbill-0.24.21/jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/AdminResource.java
