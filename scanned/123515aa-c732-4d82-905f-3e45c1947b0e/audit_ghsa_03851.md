# [H] Insufficiently Protected Credentials in Pivotal Reactor Netty

## Summary
Severity: High
Advisory: GHSA-j52r-xc68-q8f4
CVE: CVE-2019-11284
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-10-23
Source: https://github.com/advisories/GHSA-j52r-xc68-q8f4
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty` — affected >=0 <0.8.11

## Details
Pivotal Reactor Netty, versions prior to 0.8.11, passes headers through redirects, including authorization ones. A remote unauthenticated malicious user may gain access to credentials for a different server than they have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11284
- https://pivotal.io/security/cve-2019-11284
