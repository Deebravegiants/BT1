# [M] Cross-site Scripting In Apache Brooklyn

## Summary
Severity: Medium
Advisory: GHSA-j3g9-3fvv-gqfp
CVE: CVE-2017-3165
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j3g9-3fvv-gqfp
Type: github-advisory

## Affected
- Maven: `org.apache.brooklyn:brooklyn` — affected >=0 <0.10.0

## Details
In Apache Brooklyn before 0.10.0, the REST server is vulnerable to cross-site scripting where one authenticated user can cause scripts to run in the browser of another user authorized to access the first user's resources. This is due to improper escaping of server-side content. There is known to be a proof-of-concept exploit using this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3165
- https://brooklyn.apache.org/community/security/CVE-2017-3165.html
- https://lists.apache.org/thread.html/5aa6b7583edbfc1f5653607003204326d9e27ef65e8af356c798b21c@%3Cdev.brooklyn.apache.org%3E
- http://www.securityfocus.com/bid/96228
