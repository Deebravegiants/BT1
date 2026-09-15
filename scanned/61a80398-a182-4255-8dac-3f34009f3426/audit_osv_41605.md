# [M] Frappe: Mass assignment via set_value

## Summary
Severity: Medium
Advisory: CVE-2026-62315
Aliases: GHSA-2c6h-wv85-fxvj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-62315
Type: osv

## Details
Frappe is a full-stack web application framework. In version 16.31.0 and earlier, frappe.client.set_value in frappe/client.py checks a dictionary supplied through the fieldname parameter against forbidden standard and child-table fields before parsing the dictionary into individual field names. An authenticated caller can exploit this type confusion to mass-assign protected fields through the client endpoint. No released fixed version is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62315.json
- https://github.com/frappe/frappe/security/advisories/GHSA-2c6h-wv85-fxvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-62315
- https://github.com/frappe/frappe/commit/2a04fae9353c02f0a9ce9f40f92c1eba6765c77b
- https://github.com/frappe/frappe/pull/38951
