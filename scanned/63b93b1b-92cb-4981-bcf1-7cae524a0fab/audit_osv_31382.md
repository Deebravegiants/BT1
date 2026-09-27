# [M] Stack Exhaustion In Tensorflow Serving

## Summary
Severity: Medium
Advisory: CVE-2025-0649
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2025-05-06
Source: https://osv.dev/vulnerability/CVE-2025-0649
Type: osv

## Details
Incorrect JSON input stringification in Google's Tensorflow serving versions up to 2.18.0 allows for potentially unbounded recursion leading to server crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0649.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0649
- https://github.com/tensorflow/serving/commit/6cb013167d13f2ed3930aabb86dbc2c8c53f5adf
