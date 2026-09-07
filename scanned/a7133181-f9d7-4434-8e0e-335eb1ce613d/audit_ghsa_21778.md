# [H] Exposure of Sensitive Information to an Unauthorized Actor in Concord

## Summary
Severity: High
Advisory: GHSA-6566-9526-52v6
CVE: CVE-2020-10591
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-6566-9526-52v6
Type: github-advisory

## Affected
- Maven: `com.walmartlabs.concord:concord-common` — affected >=0 <1.44.0

## Details
An issue was discovered in Walmart Labs Concord before 1.44.0. CORS Access-Control-Allow-Origin headers have a potentially unsafe dependency on Origin headers, and are not configurable. This allows remote attackers to discover host information, nodes, API metadata, and references to usernames via api/v1/apikey.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10591
- https://github.com/walmartlabs/concord/issues/22
- https://github.com/walmartlabs/concord
- https://github.com/walmartlabs/concord/compare/1.43.0...1.44.0
