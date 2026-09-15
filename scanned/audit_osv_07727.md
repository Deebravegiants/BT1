# [H] Apache Tomcat: Bad ornext processing in RewriteValve

## Summary
Severity: High
Advisory: BIT-tomcat-2026-53404
Aliases: CVE-2026-53404
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-53404
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.5

## Details
Always-Incorrect Control Flow Implementation vulnerability in Apache Tomcat's rewrite valve meant that if the first condition in an OR chain matched, subsequent non-OR conditions were skipped.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.22, from 10.1.0 through 10.1.55, from 9.0.0 through 9.0.118, from 8.5.0 through 8.5.100. Other versions that have reached end of support may also be affected.

Users are recommended to upgrade to version 11.0.23, 10.1.56 or 9.0.119, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/21
- https://lists.apache.org/thread/rdhpghgfskrdmw9hqzjgjrtw538smpmz
- https://nvd.nist.gov/vuln/detail/CVE-2026-53404
