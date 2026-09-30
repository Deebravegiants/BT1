# [M] CVE-2026-38533

## Summary
Severity: Medium
Advisory: CVE-2026-38533
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-38533
Type: osv

## Details
An improper authorization vulnerability in the /api/v1/users/{id} endpoint of Snipe-IT v8.4.0 allows authenticated attackers with the users.edit permission to modify sensitive authentication and account-state fields of other non-admin users via supplying a crafted PUT request.

## References
- https://github.com/TREXNEGRO/Security-Advisories/tree/main/CVE-2026-38533
- https://snipeitapp.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38533
- https://github.com/TREXNEGRO/Security-Advisories/blob/main/CVE-2026-38533/poc.md
