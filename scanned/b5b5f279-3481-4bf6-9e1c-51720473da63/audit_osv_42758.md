# [C] CVE-2026-71193

## Summary
Severity: Critical
Advisory: CVE-2026-71193
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-71193
Type: osv

## Details
In OpenStack Designate before 22.0.1, zone creation checks (_is_subzone, _is_superzone, and the duplicate-zone DB constraint) are scoped to the target pool only. An authenticated user can bypass these checks by scheduling a zone to a different pool via the AttributeFilter scheduler, creating an overlapping zone that conflicts with another tenant's zone. This enables cross-tenant DNS hijack (redirecting traffic to attacker-controlled IPs) and DNS denial of service (NODATA responses). Exploitation requires a multi-pool deployment with AttributeFilter enabled in scheduler_filters, which is a non-default but documented and supported configuration for self-service tiering.

## References
- https://opendev.org/openstack/designate
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71193.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71193
- https://security.openstack.org/ossa/OSSA-2026-034.html
- https://www.openwall.com/lists/oss-security/2026/08/11/6
- https://launchpad.net/bugs/2160533
