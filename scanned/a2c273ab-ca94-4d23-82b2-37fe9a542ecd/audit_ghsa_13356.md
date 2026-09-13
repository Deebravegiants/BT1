# [H] Jenkins Pipeline restFul API Plugin vulnerable to Cross Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-hmw6-r547-42fr
CVE: CVE-2023-37957
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-hmw6-r547-42fr
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:pipeline-restful-api` — affected >=0

## Details
Jenkins Pipeline restFul API Plugin 0.11 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to have Jenkins connect to an attacker-specified URL, capturing a newly generated JCLI token that allows impersonating the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37957
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3126
- http://www.openwall.com/lists/oss-security/2023/07/12/2
