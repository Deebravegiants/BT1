# [C] Apache SOAP contains unauthenticated RPCRouterServlet

## Summary
Severity: Critical
Advisory: GHSA-789v-h9hw-38pg
CVE: CVE-2022-45378
CWE: CWE-287, CWE-306, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-14
Source: https://github.com/advisories/GHSA-789v-h9hw-38pg
Type: github-advisory

## Affected
- Maven: `soap:soap` — affected >=0.0.0

## Details
** UNSUPPORTED WHEN ASSIGNED ** In the default configuration of Apache SOAP, an RPCRouterServlet is available without authentication. This gives an attacker the possibility to invoke methods on the classpath that meet certain criteria. Depending on what classes are available on the classpath this might even lead to arbitrary remote code execution. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45378
- https://lists.apache.org/thread/g4l64s283njhnph2otx7q4gs2j952d31
- http://www.openwall.com/lists/oss-security/2022/11/14/4
