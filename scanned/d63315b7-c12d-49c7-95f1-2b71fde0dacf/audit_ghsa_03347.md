# [H] Denial of Service (DoS) in restify-paginate

## Summary
Severity: High
Advisory: GHSA-qr9h-vr5p-pwwx
CVE: CVE-2020-27543
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-12
Source: https://github.com/advisories/GHSA-qr9h-vr5p-pwwx
Type: github-advisory

## Affected
- npm: `restify-paginate` — affected >=0

## Details
The restify-paginate package 0.0.5 for Node.js allows remote attackers to cause a Denial-of-Service by omitting the HTTP Host header. A Restify-based web service would crash with an uncaught exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27543
- https://github.com/paulvarache/restify-paginate
- https://github.com/secoats/cve/tree/master/CVE-2020-27543_dos_restify-paginate
- https://security.netapp.com/advisory/ntap-20210401-0002
- https://www.npmjs.com/package/restify-paginate
