# [M] Issue in Anomaly Detection with document and field level rules in numerical feature aggregations

## Summary
Severity: Medium
Advisory: CVE-2023-23933
Aliases: GHSA-47qw-jwpx-pp4c
CVSS: 5.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/CVE-2023-23933
Type: osv

## Details
OpenSearch Anomaly Detection identifies atypical data and receives automatic notifications. There is an issue with the application of document and field level restrictions in the Anomaly Detection plugin, where users with the Anomaly Detector role can read aggregated numerical data (e.g. averages, sums) of fields that are otherwise restricted to them. This issue only affects authenticated users who were previously granted read access to the indexes containing the restricted fields. This issue has been patched in versions 1.3.8 and 2.6.0. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23933.json
- https://github.com/opensearch-project/anomaly-detection/security/advisories/GHSA-47qw-jwpx-pp4c
- https://nvd.nist.gov/vuln/detail/CVE-2023-23933
