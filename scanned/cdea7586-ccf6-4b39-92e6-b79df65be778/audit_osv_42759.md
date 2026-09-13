# [M] CVE-2026-71194

## Summary
Severity: Medium
Advisory: CVE-2026-71194
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-71194
Type: osv

## Details
In OpenStack Designate before 22.0.2, the mDNS handler performs pool-blind lookups when resolving record queries and NOTIFY requests. When two zones with the same name exist across different pools, the lookup fails with a deterministic error, causing the handler to return REFUSED for all DNS queries through that path. The _handle_notify path is exploitable via a single unauthenticated UDP packet. This is independently reachable through the cross-tenant zone overlap described in a different recent CVE, and also affects legitimate same-tenant cross-pool configurations. BIND9 views do not mitigate this issue as mDNS is a shared service upstream of any view configuration.

## References
- https://opendev.org/openstack/designate
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71194.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71194
- https://security.openstack.org/ossa/OSSA-2026-034.html
- https://launchpad.net/bugs/2160533
- https://www.openwall.com/lists/oss-security/2026/08/11/6
