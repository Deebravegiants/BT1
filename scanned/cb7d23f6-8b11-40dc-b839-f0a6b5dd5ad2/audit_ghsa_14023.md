# [H] Cross Site Scripting in OpenTSDB

## Summary
Severity: High
Advisory: GHSA-9chv-3w6c-jq9w
CVE: CVE-2023-25827
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-05-03
Source: https://github.com/advisories/GHSA-9chv-3w6c-jq9w
Type: github-advisory

## Affected
- Maven: `net.opentsdb:opentsdb` — affected >=0

## Details
Due to insufficient validation of parameters reflected in error messages by the legacy HTTP query API and the logging endpoint, it is possible to inject and execute malicious JavaScript within the browser of a targeted OpenTSDB user. This issue shares the same root cause as CVE-2018-13003, a reflected XSS vulnerability with the suggestion endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25827
- https://github.com/OpenTSDB/opentsdb/pull/2274
- https://github.com/OpenTSDB/opentsdb
- https://www.synopsys.com/blogs/software-security/opentsdb
