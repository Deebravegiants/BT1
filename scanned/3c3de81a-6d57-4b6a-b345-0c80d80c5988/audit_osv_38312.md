# [C] CVE-2026-38429

## Summary
Severity: Critical
Advisory: CVE-2026-38429
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-38429
Type: osv

## Details
OpenCMS v20 and before is vulnerable to XML External Entity (XXE) in the Admin Import DB feature due to insecure XML parsing of user supplied .zip files containing a manifest.xml.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38429.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38429
- https://github.com/alkacon/opencms-core/commit/e3e41e5a96d71383279e7d23c627efc9934008c1
