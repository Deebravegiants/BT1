# [H] Apache Struts Improper Control of Dynamically-Managed Code Resources vulnerability

## Summary
Severity: High
Advisory: GHSA-729q-fcgp-r5xh
CVE: CVE-2023-41835
CWE: CWE-459
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-729q-fcgp-r5xh
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=6.2.0 <6.3.0.1
- Maven: `org.apache.struts:struts2-core` — affected >=6.0.0 <6.1.2.2
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.5.32

## Details
When a Multipart request is performed but some of the fields exceed the maxStringLength limit, the upload files will remain in struts.multipart.saveDir even if the request has been denied.
Users are recommended to upgrade to versions Struts 2.5.32 or 6.1.2.2 or Struts 6.3.0.1 or greater, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41835
- https://github.com/apache/struts/commit/3292152f8c0a77ee4827beede82b6580478a2c2a
- https://github.com/apache/struts/commit/4c044f12560e22e00520595412830f9582d6dac7
- https://github.com/apache/struts/commit/bf54436869c264941dd192c752a4abfaa65d3711
- https://github.com/apache/struts
- https://lists.apache.org/thread/6wj530kh3ono8phr642y9sqkl67ys2ft
- https://security.netapp.com/advisory/ntap-20231013-0001
- https://www.openwall.com/lists/oss-security/2023/12/09/1
- http://www.openwall.com/lists/oss-security/2023/12/09/1
