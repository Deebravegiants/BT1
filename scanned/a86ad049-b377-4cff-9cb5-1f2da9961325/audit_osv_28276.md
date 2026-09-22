# [C] CVE-2024-30896

## Summary
Severity: Critical
Advisory: CVE-2024-30896
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-30896
Type: osv

## Details
InfluxDB OSS 2.x through 2.7.11 stores the administrative operator token under the default organization which allows authorized users with read access to the authorization resource of the default organization to retrieve the operator token. InfluxDB OSS 1.x, Enterprise, Cloud, Cloud Dedicated and Clustered are not affected. NOTE: The researcher states that InfluxDB allows allAccess administrators to retrieve all raw tokens via an "influx auth ls" command. The supplier indicates that the organizations feature is operating as intended and that users may choose to add users to non-default organizations. A future release of InfluxDB 2.x will remove the ability to retrieve tokens from the API. The supplier has stated that InfluxDB 2.8.0 has addressed this issue.

## References
- https://github.com/influxdata/influxdb/releases/tag/v2.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30896.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-30896
- https://github.com/influxdata/influxdb/issues/24797
- https://github.com/XenoM0rph97/CVE-2024-30896
