# [H] LORIS has a path traversal in static router

## Summary
Severity: High
Advisory: CVE-2026-34392
Aliases: GHSA-rfj5-58hv-wc5f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-34392
Type: osv

## Details
LORIS (Longitudinal Online Research and Imaging System) is a self-hosted web application that provides data- and project-management for neuroimaging research. From 20.0.0 to before 27.0.3 and 28.0.1, a bug in the static file router can allow an attacker to traverse outside of the intended directory, allowing unintended files to be downloaded through the static, css, and js endpoints. This vulnerability is fixed in 27.0.3 and 28.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34392.json
- https://github.com/aces/Loris/security/advisories/GHSA-rfj5-58hv-wc5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34392
