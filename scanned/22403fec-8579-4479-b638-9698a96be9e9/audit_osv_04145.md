# [H] Apache APISIX: basic-auth logs plaintext credentials at info level

## Summary
Severity: High
Advisory: BIT-apisix-2025-62232
Aliases: CVE-2025-62232
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-apisix-2025-62232
Type: osv

## Affected
- Bitnami: `apisix` — affected >=1.0.0 <3.14.0

## Details
Sensitive data exposure via logging in basic-auth leads to plaintext usernames and passwords written to error logs and forwarded to log sinks when log level is INFO/DEBUG. This creates a high risk of credential compromise through log access.
It has been fixed in the following commit:  https://github.com/apache/apisix/pull/12629 
Users are recommended to upgrade to version 3.14, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2025/10/30/4
- https://lists.apache.org/thread/32hdgh570btfhg02hfc7p7ckf9v83259
- https://nvd.nist.gov/vuln/detail/CVE-2025-62232
