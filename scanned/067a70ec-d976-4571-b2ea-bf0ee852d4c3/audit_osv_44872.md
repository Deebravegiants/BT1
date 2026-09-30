# [M] CVE-2026-87803

## Summary
Severity: Medium
Advisory: CVE-2026-87803
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-87803
Type: osv

## Details
An authorization bypass vulnerability exists in the Countly Server DBViewer due to flawed sub-pipeline detection in the aggregation stage sanitizer. The /o/db aggregation endpoint parses user-controlled aggregation JSON and passes it through a stage sanitizer that determines whether a nested array is a sub-pipeline by checking if every element contains a key present in a hardcoded KNOWN_STAGE_OPERATORS set. If any element contains an unrecognized stage key, such as the undocumented MongoDB-internal $_internalInhibitOptimization, the sanitizer misclassifies the entire branch as a generic array and skips stage-level stripping for all sibling stages. This allows a non-admin user with DBViewer read permission to inject forbidden operators like $lookup inside $facet sub-pipelines, performing cross-collection joins into restricted collections. This leads to unauthorized read access to sensitive data including password-reset tokens (prid), enabling account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87803.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-87803
- https://github.com/Countly/countly-server/pull/7868
