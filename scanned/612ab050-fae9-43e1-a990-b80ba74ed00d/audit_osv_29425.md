# [H] GHSL-2023-256: HertzBeat Authenticated (guest role) SQL injection in /api/monitor/{monitorId}/metric/{metricFull}

## Summary
Severity: High
Advisory: CVE-2024-42361
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-42361
Type: osv

## Details
Hertzbeat is an open source, real-time monitoring system. Hertzbeat 1.6.0 and earlier declares a /api/monitor/{monitorId}/metric/{metricFull} endpoint to download job metrics. In the process, it executes a SQL query with user-controlled data, allowing for SQL injection.

## References
- https://github.com/dromara/hertzbeat/blob/1f12ac9f2a1a3d86b1d476775e14174243b250a8/manager/src/main/java/org/dromara/hertzbeat/manager/controller/MonitorsController.java#L202
- https://github.com/dromara/hertzbeat/blob/1f12ac9f2a1a3d86b1d476775e14174243b250a8/warehouse/src/main/java/org/dromara/hertzbeat/warehouse/store/HistoryTdEngineDataStorage.java#L242
- https://github.com/dromara/hertzbeat/blob/1f12ac9f2a1a3d86b1d476775e14174243b250a8/warehouse/src/main/java/org/dromara/hertzbeat/warehouse/store/HistoryTdEngineDataStorage.java#L295
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42361.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42361
- https://securitylab.github.com/advisories/GHSL-2023-254_GHSL-2023-256_HertzBeat/
