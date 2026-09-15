# [M] DataEase has database configuration information exposure vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-30269
Aliases: GHSA-8gvx-4qvj-6vv5
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-30269
Type: osv

## Details
DataEase, an open source data visualization and analysis tool, has a database configuration information exposure vulnerability prior to version 2.5.0. Visiting the `/de2api/engine/getEngine;.js` path via a browser reveals that the platform's database configuration is returned. The vulnerability has been fixed in v2.5.0. No known workarounds are available aside from upgrading.

## References
- https://github.com/dataease/dataease/releases/tag/v2.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30269.json
- https://github.com/dataease/dataease/security/advisories/GHSA-8gvx-4qvj-6vv5
- https://nvd.nist.gov/vuln/detail/CVE-2024-30269
