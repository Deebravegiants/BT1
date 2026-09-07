# [H] Keystone is vulnerable to CSV injection

## Summary
Severity: High
Advisory: GHSA-6494-v9fq-fgq2
CVE: CVE-2017-15879
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-16
Source: https://github.com/advisories/GHSA-6494-v9fq-fgq2
Type: github-advisory

## Affected
- npm: `keystone` — affected >=0 <4.0.0-beta7

## Details
CSV Injection (aka Excel Macro Injection or Formula Injection) exists in admin/server/api/download.js and lib/list/getCSVData.js in KeystoneJS before 4.0.0-beta.7 via a value that is mishandled in a CSV export.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15879
- https://github.com/keystonejs/keystone/pull/4478
- https://github.com/advisories/GHSA-6494-v9fq-fgq2
- https://packetstormsecurity.com/files/144755/KeystoneJS-4.0.0-beta.5-Unauthenticated-CSV-Injection.html
- https://www.exploit-db.com/exploits/43053
