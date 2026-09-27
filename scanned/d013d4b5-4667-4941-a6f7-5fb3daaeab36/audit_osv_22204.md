# [M] Pi-Hole/AdminLTE vulnerable due to improper access control in queryads endpoint

## Summary
Severity: Medium
Advisory: CVE-2022-23513
Aliases: GHSA-6qh8-6rrj-7497
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-23513
Type: osv

## Details
Pi-Hole is a network-wide ad blocking via your own Linux hardware, AdminLTE is a Pi-hole Dashboard for stats and more. In case of an attack, the threat actor will obtain the ability to perform an unauthorized query for blocked domains on  `queryads` endpoint. In the case of application, this vulnerability exists because of a lack of validation in code on a root server path:
`/admin/scripts/pi-hole/phpqueryads.php.` Potential threat actor(s) are able to perform an unauthorized query search in blocked domain lists. This could lead to the disclosure for any victims' personal blacklists.

## References
- http://packetstormsecurity.com/files/174460/AdminLTE-PiHole-Broken-Access-Control.html
- https://github.com/pi-hole/AdminLTE/releases/tag/v5.18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23513.json
- https://github.com/pi-hole/AdminLTE/security/advisories/GHSA-6qh8-6rrj-7497
- https://nvd.nist.gov/vuln/detail/CVE-2022-23513
