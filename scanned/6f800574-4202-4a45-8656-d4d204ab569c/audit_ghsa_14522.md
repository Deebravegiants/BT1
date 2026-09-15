# [H] Improper Input Validation In Eclipse BIRT

## Summary
Severity: High
Advisory: GHSA-4grc-q4fj-45p8
CVE: CVE-2023-0100
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-15
Source: https://github.com/advisories/GHSA-4grc-q4fj-45p8
Type: github-advisory

## Affected
- Maven: `org.eclipse.birt:org.eclipse.birt.report.viewer` — affected >=2.6.2 <4.13

## Details
In Eclipse BIRT, starting from version 2.6.2, the default configuration allowed to retrieve a report from the same host using an absolute HTTP path for the report parameter (e.g. __report=http://xyz.com/report.rptdesign). If the host indicated in the __report parameter matched the HTTP Host header value, the report would be retrieved. However, the Host header can be tampered with on some configurations where no virtual hosts are put in place (e.g. in the default configuration of Apache Tomcat) or when the default host points to the BIRT server. This vulnerability was patched on Eclipse BIRT 4.13.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0100
- https://github.com/eclipse/birt/pull/1165
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=580391
- https://github.com/eclipse/birt
