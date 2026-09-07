# [M] Cross-site Scripting in Eclipse Hawkbit

## Summary
Severity: Medium
Advisory: GHSA-rcvx-rmvf-mxch
CVE: CVE-2020-27219
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-rcvx-rmvf-mxch
Type: github-advisory

## Affected
- Maven: `org.eclipse.hawkbit:hawkbit-parent` — affected >=0 <0.3.0M7

## Details
In all version of Eclipse Hawkbit prior to 0.3.0M7, the HTTP 404 (Not Found) JSON response body returned by the REST API may contain unsafe characters within the path attribute. Sending a POST request to a non existing resource will return the full path from the given URL unescaped to the client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27219
- https://github.com/eclipse/hawkbit/issues/1067
- https://github.com/eclipse/hawkbit/commit/94b7c12cde1b38eda5414bd88d6d068008cfb9f9
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=570289
