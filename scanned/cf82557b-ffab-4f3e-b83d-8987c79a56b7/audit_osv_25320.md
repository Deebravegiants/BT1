# [C] DataEase data source has deserialization vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-33963
Aliases: GHSA-m26j-gh4m-xh9f
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-33963
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to version 1.18.7, a deserialization vulnerability exists in the DataEase datasource, which can be exploited to execute arbitrary code. The vulnerability has been fixed in v1.18.7. There are no known workarounds aside from upgrading.

## References
- https://github.com/dataease/dataease/releases/tag/v1.18.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33963.json
- https://github.com/dataease/dataease/security/advisories/GHSA-m26j-gh4m-xh9f
- https://nvd.nist.gov/vuln/detail/CVE-2023-33963
