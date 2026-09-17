# [H] InvenTree Vulnerable to ORM Filter Injection

## Summary
Severity: High
Advisory: CVE-2026-33530
Aliases: GHSA-m8j2-vfmq-p6qg
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33530
Type: osv

## Details
InvenTree is an Open Source Inventory Management System. Prior to version 1.2.6, certain API endpoints associated with bulk data operations can be hijacked to exfiltrate sensitive information from the database. The bulk operation API endpoints (e.g. `/api/part/`, `/api/stock/`, `/api/order/so/allocation/`, and others) accept a filters parameter that is passed directly to Django's ORM queryset.filter(**filters) without any field allowlisting. This enables any authenticated user to traverse model relationships using Django's __ lookup syntax and perform blind boolean-based data extraction. This issue is patched in version 1.2.6, and 1.3.0 (or above). Users should update to the patched versions. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33530.json
- https://github.com/inventree/InvenTree/security/advisories/GHSA-m8j2-vfmq-p6qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33530
- https://github.com/inventree/InvenTree/pull/11581
