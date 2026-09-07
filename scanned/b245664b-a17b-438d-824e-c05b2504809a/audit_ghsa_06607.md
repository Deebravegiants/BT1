# [M] Apache HttpComponents Client: Connection Leak on Content-Encoding Decode Error Leads to Pool Exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-hjcp-jmpx-g3qm
CVE: CVE-2026-64607
CWE: CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-hjcp-jmpx-g3qm
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents.client5:httpclient5` — affected >=5.0-alpha1 <5.6.3

## Details
HttpClient based on the classic i/o model fails to correctly release the underlying connection back to the connection manager if it encounters an invalid or unsupported `Content-Encoding` header value in the response message. Please note this defect does not affect HttpClient based on the async i/o model.

This issue affects Apache HttpComponents Client: from 5.0-alpha1 through 5.6.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-64607
- https://github.com/apache/httpcomponents-client/commit/55733f4121f7ba26ddf04fe12739d9c15962cb94
- https://github.com/apache/httpcomponents-client/commit/ebac9512f555c4a355cad3f59ef2db69b597cc97
- https://github.com/apache/httpcomponents-client
- https://github.com/apache/httpcomponents-client/releases/tag/rel/v5.6.3
- https://github.com/apache/httpcomponents-client/releases/tag/rel/v5.7-alpha1
- https://lists.apache.org/thread/qqfzo3fqcdk4l5496vz95ppvl4ty511q
- http://www.openwall.com/lists/oss-security/2026/08/13/5
