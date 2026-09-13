# [M] CVE-2026-45819

## Summary
Severity: Medium
Advisory: CVE-2026-45819
Aliases: GHSA-w5vr-8v7q-w6rv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/S:N/AU:Y/R:U/V:D/RE:M/U:Amber)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-45819
Type: osv

## Details
baseline-browser-mapping 2.x before 2.11.0 calls process.exit() instead of throwing on invalid or conflicting input parameters, and can trigger immediate process termination, causing denial of service.

## References
- https://github.com/web-platform-dx/baseline-browser-mapping/blob/b7881aa61c8a057e24468ab5ee18c5ecedbbf691/src/index.ts#L142
- https://www.npmjs.com/package/baseline-browser-mapping
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45819.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45819
- https://github.com/web-platform-dx/baseline-browser-mapping/pull/137/changes#diff-7ae45ad102eab3b6d7e7896acd08c427a9b25b346470d7bc6507b6481575d519
