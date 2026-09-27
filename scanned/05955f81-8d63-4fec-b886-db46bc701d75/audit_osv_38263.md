# [M] SSRF via Referer header in ChurchCRM allows server-side HTTP/HTTPS requests to arbitrary hosts

## Summary
Severity: Medium
Advisory: CVE-2026-35572
Aliases: GHSA-44x3-28jv-mrwq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35572
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 6.5.3, it is possible to trigger server-side HTTP/HTTPS requests to arbitrary hosts (SSRF) by supplying a crafted URL in the Referer request header. The server subsequently makes an outbound request to the attacker-controlled domain, confirmed via OAST. This vulnerability is fixed in 6.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35572.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-44x3-28jv-mrwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-35572
