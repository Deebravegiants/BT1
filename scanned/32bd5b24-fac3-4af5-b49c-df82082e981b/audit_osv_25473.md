# [H] DataEase has a SQL injection vulnerability that can bypass blacklists

## Summary
Severity: High
Advisory: CVE-2023-37258
Aliases: GHSA-r39x-fcc6-47g4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/CVE-2023-37258
Type: osv

## Details
DataEase is an open source data visualization analysis tool. Prior to version 1.18.9, DataEase has a SQL injection vulnerability that can bypass blacklists. The vulnerability has been fixed in v1.18.9. There are no known workarounds.

## References
- https://github.com/dataease/dataease/blob/dev/backend/src/main/java/io/dataease/controller/panel/AppLogController.java#L41
- https://github.com/dataease/dataease/blob/dev/backend/src/main/java/io/dataease/ext/ExtDataSourceMapper.java
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37258.json
- https://github.com/dataease/dataease/security/advisories/GHSA-r39x-fcc6-47g4
- https://nvd.nist.gov/vuln/detail/CVE-2023-37258
