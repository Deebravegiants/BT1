# [M] Missing Log Aggregation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

There is no centralized system that gathers operational events of AWS stack components. This includes S3 server access logs, configuration changes, as well as Cloudfront-related logging.

#### Recommendation

It is recommended to enable CloudTrail for internal log aggregation as it integrates seamlessly with S3, Cloudfront, and IAM. Furthermore, regular reviews should be set up where system activity is checked to detect suspicious activity as soon as possible.
