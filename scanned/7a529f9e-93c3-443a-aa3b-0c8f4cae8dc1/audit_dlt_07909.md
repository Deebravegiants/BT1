# [?] CI: nancy ignore CVE-2024-8421 (#2695)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2024-09-10
Source: https://github.com/bnb-chain/bsc/commit/7de27ca9e94e08af4a0b8aa35fa94e29c12607d0
Type: security-commit

## Details
CI: nancy ignore CVE-2024-8421 (#2695)

## Patch
### .nancy-ignore
```diff
@@ -1,2 +1,3 @@
 CVE-2024-34478 # "CWE-754: Improper Check for Unusual or Exceptional Conditions." This vulnerability is BTC only, BSC does not have the issue.
 CVE-2024-6104 # "CWE-532: Information Exposure Through Log Files" This is caused by the vulnerabilities go-retryablehttp@v0.7.4, it is only used in cmd devp2p, impact is limited. will upgrade to v0.7.7 later
+CVE-2024-8421 # "CWE-400: Uncontrolled Resource Consumption (Resource Exhaustion)" This vulnerability is caused by issues in the golang.org/x/net package. Even the latest version(v0.29.0) has not yet addressed it, but we will continue to monitor updates closely.
\ No newline at end of file
```
