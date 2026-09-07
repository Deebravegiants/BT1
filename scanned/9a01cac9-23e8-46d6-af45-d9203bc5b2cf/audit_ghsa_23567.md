# [C] Cloud Foundry vulnerable to Cross-Site Request Forgery

## Summary
Severity: Critical
Advisory: GHSA-4m8c-h7fr-gq5c
CVE: CVE-2016-6637
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4m8c-h7fr-gq5c
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=2.0.0 <2.7.4.7
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.0.0 <3.3.0.5
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.4.0 <3.4.4
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.5.0 <3.7.0

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in Pivotal Cloud Foundry (PCF) before 242; UAA 2.x before 2.7.4.7, 3.x before 3.3.0.5, and 3.4.x before 3.4.4; UAA BOSH before 11.5 and 12.x before 12.5; Elastic Runtime before 1.6.40, 1.7.x before 1.7.21, and 1.8.x before 1.8.2; and Ops Manager 1.7.x before 1.7.13 and 1.8.x before 1.8.1 allow remote attackers to hijack the authentication of unspecified victims for requests that approve or deny a scope via a profile or authorize approval page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6637
- https://github.com/cloudfoundry/uaa/commit/37e0384c52d3337a3fa4eef6647032229edecfa4
- https://github.com/cloudfoundry/uaa/commit/cded6164a3b90e791688a954069aea3cfde59b69
- https://github.com/cloudfoundry/uaa/commit/f3d8a9e1ee1acac5bf1f8487ac9461f4cf4505c
- https://pivotal.io/security/cve-2016-6637
- https://web.archive.org/web/20200227221542/http://www.securityfocus.com/bid/93245
