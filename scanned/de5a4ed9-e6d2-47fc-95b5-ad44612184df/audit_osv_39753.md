# [H] Frappe: Host header poisoning can redirect magic login links to an attacker-controlled domain

## Summary
Severity: High
Advisory: CVE-2026-47194
Aliases: GHSA-3w78-3cj3-p949
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-47194
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 15.108.0 and 16.18.3, temporary magic login link generation can use an attacker-controlled request Host header, allowing a remote attacker to cause emailed login links to point to an attacker-controlled domain and capture the login token when a recipient follows the link. This issue is fixed in versions 15.108.0 and 16.18.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47194.json
- https://github.com/frappe/frappe/security/advisories/GHSA-3w78-3cj3-p949
- https://nvd.nist.gov/vuln/detail/CVE-2026-47194
