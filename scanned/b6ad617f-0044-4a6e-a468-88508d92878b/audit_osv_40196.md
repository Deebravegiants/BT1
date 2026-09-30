# [M] CVE-2026-50744

## Summary
Severity: Medium
Advisory: CVE-2026-50744
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-50744
Type: osv

## Details
A bypass to the admin‑only restriction of the XML‑RPC API in Revive Adserver 6.0.7. The API response for the ox.login method returned a session ID cookie in the HTTP headers, and although the method correctly returned an error, the associated session was not invalidated. As a result, the leaked session ID could be used to perform subsequent API calls without restrictions.

## References
- https://hackerone.com/reports/3783738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50744.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50744
