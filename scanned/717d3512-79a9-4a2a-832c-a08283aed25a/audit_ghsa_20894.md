# [H] Apache SOAP's RPCRouterServlet allows reading of arbitrary files over HTTP

## Summary
Severity: High
Advisory: GHSA-jq8c-j47c-vvwm
CVE: CVE-2022-40705
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-jq8c-j47c-vvwm
Type: github-advisory

## Affected
- Maven: `soap:soap` — affected >=2.2

## Details
An Improper Restriction of XML External Entity Reference vulnerability in RPCRouterServlet of Apache SOAP allows an attacker to read arbitrary files over HTTP. This issue affects Apache SOAP version 2.2 and later versions. It is unknown whether previous versions are also affected. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40705
- https://lists.apache.org/thread/02yo04w93rdjmllz4454lvodn5xzhwhl
- http://www.openwall.com/lists/oss-security/2022/09/22/1
