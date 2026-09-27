# [M] TorchServe script references S3 bucket without ensuring ownership or confirming accessibility

## Summary
Severity: Medium
Advisory: GHSA-xx7c-j7h3-vjcq
CVE: CVE-2024-6577
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-xx7c-j7h3-vjcq
Type: github-advisory

## Affected
- PyPI: `torchserve` — affected >=0

## Details
In the latest version of pytorch/serve, the script 'upload_results_to_s3.sh' references the S3 bucket 'benchmarkai-metrics-prod' without ensuring its ownership or confirming its accessibility. This could lead to potential security vulnerabilities or unauthorized access to the bucket if it is not properly secured or claimed by the appropriate entity. The issue may result in data breaches, exposure of proprietary information, or unauthorized modifications to stored data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6577
- https://github.com/pytorch/serve
- https://huntr.com/bounties/20917570-8328-428f-bd1d-4fcd71fb2359
