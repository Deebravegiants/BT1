# [M] Apache APISIX: Forward-Auth Request Smuggling

## Summary
Severity: Medium
Advisory: BIT-apisix-2024-32638
Aliases: CVE-2024-32638
Ecosystem: Bitnami
Published: 2024-05-04
Source: https://osv.dev/vulnerability/BIT-apisix-2024-32638
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.8.0 <3.9.1

## Details
Inconsistent Interpretation of HTTP Requests ('HTTP Request Smuggling') vulnerability in Apache APISIX when using `forward-auth` plugin.This issue affects Apache APISIX: from 3.8.0, 3.9.0.

Users are recommended to upgrade to version 3.8.1, 3.9.1 or higher, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/05/02/2
- https://lists.apache.org/thread/ngvgxllw4zn4hgngkqw2o225kf9wotov
- https://nvd.nist.gov/vuln/detail/CVE-2024-32638
