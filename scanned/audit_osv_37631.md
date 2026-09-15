# [M] Tolgee has an XXE Injection in Translation Import

## Summary
Severity: Medium
Advisory: CVE-2026-32251
Aliases: GHSA-rcvv-64pq-vxfx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-32251
Type: osv

## Details
Tolgee is an open-source localization platform. Prior to 3.166.3, the XML parsers used for importing Android XML resources (.xml) and .resx files don't disable external entity processing. An authenticated user who can import translation files into a project can exploit this to read arbitrary files from the server and make server-side requests to internal services. This vulnerability is fixed in 3.166.3.

## References
- https://github.com/tolgee/tolgee-platform/releases/tag/v3.166.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32251.json
- https://github.com/tolgee/tolgee-platform/security/advisories/GHSA-rcvv-64pq-vxfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32251
- https://github.com/tolgee/tolgee-platform/commit/7c71d5a849c9984a8c5c55b121992417442a47a5
