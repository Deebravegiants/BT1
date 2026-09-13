# [M] Label Studio through 1.23.0 Cross-Organization Storage URI Resolution

## Summary
Severity: Medium
Advisory: CVE-2026-85211
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85211
Type: osv

## Details
Label Studio fails to apply organization filters when resolving storage URIs for tasks and projects in proxy_api.py endpoints. Attackers can access other tenants' cloud storage objects by creating a separate organization and supplying arbitrary file URIs to presign or stream bucket contents.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85211.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85211
- https://www.vulncheck.com/advisories/label-studio-through-1.23.0-cross-organization-storage-uri-resolution
- https://github.com/HumanSignal/label-studio/issues/9924
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/blob/1.23.0/label_studio/io_storages/proxy_api.py
