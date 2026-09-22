# [C] HertzBeat SnakeYAML Deser RCE

## Summary
Severity: Critical
Advisory: CVE-2023-51389
Aliases: GHSA-rmvr-9p5x-mm96
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-51389
Type: osv

## Details
Hertzbeat is a real-time monitoring system. At the interface of `/define/yml`, SnakeYAML is used as a parser to parse yml content, but no security configuration is used, resulting in a YAML deserialization vulnerability. Version 1.4.1 fixes this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51389.json
- https://github.com/dromara/hertzbeat/security/advisories/GHSA-rmvr-9p5x-mm96
- https://nvd.nist.gov/vuln/detail/CVE-2023-51389
- https://github.com/dromara/hertzbeat/commit/97c3f14446d1c96d1fc993df111684926b6cce17
