# [M] NetBox 4.5.8 ORM Injection via WritableNestedSerializer

## Summary
Severity: Medium
Advisory: CVE-2026-69117
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-69117
Type: osv

## Details
NetBox 4.5.8 contains an ORM injection vulnerability that allows authenticated attackers, including those with read-only API tokens, to inject arbitrary Django ORM lookup expressions into nested object references by supplying crafted JSON dictionary keys in POST, PUT, or PATCH requests to any REST API endpoint. Attackers can exploit the unrestricted queryset used by WritableNestedSerializer to perform boolean-based blind data extraction of sensitive field values and bypass object-level permissions across all application modules including dcim, ipam, tenancy, virtualization, circuits, and extras.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69117
- https://www.vulncheck.com/advisories/netbox-orm-injection-via-writablenestedserializer
- https://github.com/netbox-community/netbox/issues/21988
- https://github.com/netbox-community/netbox/pull/22013
- https://github.com/netbox-community/netbox/commit/b3489cd529ca00703a0b7fe4c45e91539add6df6
- https://github.com/netbox-community/netbox
