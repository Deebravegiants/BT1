# [H] Apache NiFi is missing the Restricted annotation with the Execute Code Required Permission

## Summary
Severity: High
Advisory: GHSA-2j9m-25xv-mp6r
CVE: CVE-2026-39816
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-2j9m-25xv-mp6r
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-other-graph-services-nar` — affected >=2.0.0-M1 <2.9.0

## Details
The optional extension component TinkerpopClientService is missing the Restricted annotation with the Execute Code Required Permission in Apache NiFi 2.0.0-M1 through 2.8.0. The TinkerpopClientService supports configuration of ByteCode Submission for the Script Submission Type, enabling Groovy Script execution in the service prior to submitting the query. The missing Restricted annotation allows users without the Execute Code Permission to configure the Service in installations that use fine-grained authorization and have the optional TinkerpopClientService installed. Apache NiFi installations that do not have the nifi-other-graph-services-nar installed are not subject to this vulnerability. Upgrading to Apache NiFi 2.9.0 is the recommended mitigation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39816
- https://github.com/apache/nifi/pull/11108
- https://github.com/apache/nifi/commit/72fab7dde74edfd1063b57e87b0334340c1fbe93
- https://github.com/apache/nifi
- https://lists.apache.org/thread/gh9g7xwvv4l20gzff6q3367snf35ctcb
- https://zeropath.com/blog/nifi-cve-2026-39816-privesc-rce
- http://www.openwall.com/lists/oss-security/2026/04/13/8
