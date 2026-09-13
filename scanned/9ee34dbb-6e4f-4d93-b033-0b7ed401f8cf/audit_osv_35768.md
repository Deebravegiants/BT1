# [C] RCE via Deserialization in AWS Advanced JDBC Wrapper

## Summary
Severity: Critical
Advisory: CVE-2026-14265
Aliases: GHSA-c5q4-97jw-jggh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-14265
Type: osv

## Details
Deserialization of untrusted data in the RemoteQueryCachePlugin in Amazon Web Services AWS Advanced JDBC Wrapper 3.3.0 through 4.0.0 might allow an actor with write access to the shared cache infrastructure to execute arbitrary code on application servers that read cached query results via a crafted serialized Java object. The RemoteQueryCachePlugin uses ObjectInputStream without class filtering when deserializing cached query results from Redis or Valkey, enabling gadget chain execution when cache entries are poisoned.



We recommend upgrading to AWS Advanced JDBC Wrapper version 4.0.1 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-051-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14265.json
- https://github.com/aws/aws-advanced-jdbc-wrapper/security/advisories/GHSA-c5q4-97jw-jggh
- https://nvd.nist.gov/vuln/detail/CVE-2026-14265
- https://github.com/aws/aws-advanced-jdbc-wrapper/releases/tag/4.0.1
