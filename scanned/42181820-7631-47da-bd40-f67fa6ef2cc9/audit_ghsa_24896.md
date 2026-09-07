# [C] OpenTSDB vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-cx2v-jrjc-g54w
CVE: CVE-2018-12972
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cx2v-jrjc-g54w
Type: github-advisory

## Affected
- Maven: `net.opentsdb:opentsdb` — affected >=0

## Details
An issue was discovered in OpenTSDB 2.3.0. Many parameters to the /q URI can execute commands, including o, key, style, and yrange and y2range and their JSON input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12972
- https://github.com/OpenTSDB/opentsdb/issues/1239
- https://github.com/OpenTSDB/opentsdb
