# [M] CVE-2022-41712

## Summary
Severity: Medium
Advisory: CVE-2022-41712
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-41712
Type: osv

## Details
Frappe version 14.10.0 allows an external attacker to remotely obtain arbitrary local files. This is possible because the application does not correctly validate the information injected by the user in the import_file parameter.

## References
- https://github.com/frappe/frappe/
- https://fluidattacks.com/advisories/kiniza/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41712.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41712
