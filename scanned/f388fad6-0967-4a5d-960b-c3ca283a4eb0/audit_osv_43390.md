# [H] Apache Struts: Unbounded read of a JSON request body

## Summary
Severity: High
Advisory: CVE-2026-73633
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73633
Type: osv

## Details
Uncontrolled resource consumption vulnerability in the JSON plugin of Apache Struts. When an application is configured to populate actions from a JSON request body, the plugin reads that body into memory without bounding how much it will accept, so a single request can exhaust the heap and deny service to other users. The plugin's configurable JSON input length limit does not bound this read. The JSON plugin is an optional component; applications that do not use it, or use it without enabling JSON request-body handling, are not affected.

This issue affects Apache Struts: from 2.1.8 through 2.3.37, from 2.5.0 through 2.5.33, from 6.0.0 through 6.10.0, from 7.0.0 through 7.2.1.

Users are recommended to upgrade to version 6.11.0 or 7.3.0, which fixes the issue.

## References
- https://repo.maven.apache.org/maven2
- https://cwiki.apache.org/confluence/display/WW/S2-072
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73633.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73633
