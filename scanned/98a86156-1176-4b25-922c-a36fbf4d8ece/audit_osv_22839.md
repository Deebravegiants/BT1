# [H] Permission bypass due to incorrect configuration in github.com/dromara/hertzbeat

## Summary
Severity: High
Advisory: CVE-2022-39337
Aliases: GHSA-434f-f5cw-3rj6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2022-39337
Type: osv

## Details
Hertzbeat is an open source, real-time monitoring system with custom-monitoring, high performance cluster, prometheus-like and agentless. Hertzbeat versions 1.20 and prior have a permission bypass vulnerability. System authentication can be bypassed and invoke interfaces without authorization. Version 1.2.1 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39337.json
- https://github.com/dromara/hertzbeat/security/advisories/GHSA-434f-f5cw-3rj6
- https://nvd.nist.gov/vuln/detail/CVE-2022-39337
- https://github.com/dromara/hertzbeat/issues/377
- https://github.com/dromara/hertzbeat/commit/ac5970c6ceb64fafe237fc895243df5f21e40876
- https://github.com/dromara/hertzbeat/pull/382
