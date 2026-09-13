# [C] Frappe: TarSlip RCE in Package Import

## Summary
Severity: Critical
Advisory: CVE-2026-55852
Aliases: GHSA-58w2-4cjg-hvp6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55852
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 16.23.0 and 15.112.0, TarSlip RCE was possible in Package Import because tarfile members were not sufficiently checked before extraction. This issue is fixed in versions 16.23.0 and 15.112.0.

## References
- https://github.com/frappe/frappe/releases/tag/v15.112.0
- https://github.com/frappe/frappe/releases/tag/v16.23.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55852.json
- https://github.com/frappe/frappe/security/advisories/GHSA-58w2-4cjg-hvp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55852
- https://github.com/frappe/frappe/commit/3c75f13fd7d4441a880dd236450277dc37fcddfd
- https://github.com/frappe/frappe/commit/4772e3e7f72db43d48137af74fa77e5fce903223
- https://github.com/frappe/frappe/commit/57e527d933aeffaec0cd735838701792c848e3e7
- https://github.com/frappe/frappe/pull/38716
- https://github.com/frappe/frappe/pull/40044
- https://github.com/frappe/frappe/pull/40045
