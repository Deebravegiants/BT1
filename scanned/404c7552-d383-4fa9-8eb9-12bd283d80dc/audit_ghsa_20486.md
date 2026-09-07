# [M] Cross-site Scripting in Apache Knox SSO

## Summary
Severity: Medium
Advisory: GHSA-vv38-4xcj-q4rw
CVE: CVE-2021-42357
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-vv38-4xcj-q4rw
Type: github-advisory

## Affected
- Maven: `org.apache.knox:gateway-service-knoxsso` — affected >=0 <1.6.1

## Details
When using Apache Knox SSO prior to 1.6.1, a request could be crafted to redirect a user to a malicious page due to improper URL parsing. A request that included a specially crafted request parameter could be used to redirect the user to a page controlled by an attacker. This URL would need to be presented to the user outside the normal request flow through a XSS or phishing campaign.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42357
- https://lists.apache.org/thread/b7v5dkpyqb51nw0lvz4cybhgrfhk1g7j
- http://www.openwall.com/lists/oss-security/2022/01/17/2
