# [H] DataEase AWS redshift data source exists for remote code execution vulnerability

## Summary
Severity: High
Advisory: CVE-2023-28637
Aliases: GHSA-8wg2-9gwc-5fx2
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/CVE-2023-28637
Type: osv

## Details
DataEase is an open source data visualization analysis tool. In Dataease users are normally allowed to modify data and the data sources are expected to properly sanitize data. The AWS redshift data source does not provide data sanitization which may lead to remote code execution. This vulnerability has been fixed in v1.18.5. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28637.json
- https://github.com/dataease/dataease/security/advisories/GHSA-8wg2-9gwc-5fx2
- https://nvd.nist.gov/vuln/detail/CVE-2023-28637
