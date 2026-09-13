# [H] Apache Tomcat: Request smuggling via invalid chunk extension

## Summary
Severity: High
Advisory: BIT-tomcat-2026-24880
Aliases: CVE-2026-24880, GHSA-563x-q5rq-57qp
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-24880
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.20

## Details
Inconsistent Interpretation of HTTP Requests ('HTTP Request/Response Smuggling') vulnerability in Apache Tomcat via invalid chunk extension.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.18, from 10.1.0 through 10.1.52, from 9.0.0 through 9.0.115, from 8.5.0 through 8.5.100, from 7.0.0 through 7.0.109.
Other, unsupported versions may also be affected.

Users are recommended to upgrade to version 11.0.20, 10.1.52 or 9.0.116, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/09/20
- https://lists.apache.org/thread/2c682qnlg2tv4o5knlggqbl9yc2gb5sn
- https://nvd.nist.gov/vuln/detail/CVE-2026-24880
