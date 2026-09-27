# [M] Apache Shenyu Server Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7w8v-5fcq-pvqw
CVE: CVE-2023-25753
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-7w8v-5fcq-pvqw
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu-admin` — affected >=0 <2.6.0
- Maven: `org.apache.shenyu:shenyu-common` — affected >=0 <2.6.0

## Details
There exists an SSRF (Server-Side Request Forgery) vulnerability located at the `/sandbox/proxyGateway` endpoint. This vulnerability allows us to manipulate arbitrary requests and retrieve corresponding responses by inputting any URL into the requestUrl parameter.

Of particular concern is our ability to exert control over the HTTP method, cookies, IP address, and headers. This effectively grants us the capability to dispatch complete HTTP requests to hosts of our choosing.

This issue affects Apache ShenYu: 2.5.1.

Upgrade to Apache ShenYu 2.6.0 or apply patch  https://github.com/apache/shenyu/pull/4776  .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25753
- https://github.com/apache/shenyu/pull/4776
- https://github.com/apache/shenyu
- https://lists.apache.org/thread/chprswxvb22z35vnoxv9tt3zknsm977d
