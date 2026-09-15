# [M] Apache Neethi doesn't impose any restrictions on URIs when manually fetching remote policy references through the PolicyReference API

## Summary
Severity: Medium
Advisory: GHSA-287c-fxr7-3w6c
CVE: CVE-2026-42404
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-287c-fxr7-3w6c
Type: github-advisory

## Affected
- Maven: `org.apache.neethi:neethi` — affected >=0 <3.2.2

## Details
Apache Neethi does not impose any restrictions on URIs when manually fetching remote policy references through the PolicyReference API. When an application explicitly calls the API to retrieve a policy from a remote URI, an outbound request is made for arbitrary protocols and internal IP adddresses. From 3.2.2, only http or https URIs are allowed, and link-local/multicast/any-local addresses are forbidden.

Users are recommended to upgrade to version 3.2.2, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42404
- https://github.com/apache/ws-neethi
- https://lists.apache.org/thread/zdspnt64zznyjyn648553kptx69w23oq
- http://www.openwall.com/lists/oss-security/2026/05/01/8
