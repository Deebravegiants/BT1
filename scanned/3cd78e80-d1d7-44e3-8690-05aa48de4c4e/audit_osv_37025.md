# [H] Piwigo: Unauthenticated Information Disclosure via pwg.history.search API

## Summary
Severity: High
Advisory: CVE-2026-27833
Aliases: GHSA-397m-gfhm-pmg2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-27833
Type: osv

## Details
Piwigo is an open source photo gallery application for the web. Prior to version 16.3.0, the pwg.history.search API method in Piwigo is registered without the admin_only option, allowing unauthenticated users to access the full browsing history of all gallery visitors. This issue has been patched in version 16.3.0.

## References
- https://piwigo.org/release-16.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27833.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-397m-gfhm-pmg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27833
- https://github.com/Piwigo/Piwigo/commit/d05c16561ce3692ca922199f8c8d7b1a45893f1c
