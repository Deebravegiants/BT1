# [M] CSRF vulnerability in Jenkins Security Inspector plugin

## Summary
Severity: Medium
Advisory: GHSA-933x-5g7r-773q
CVE: CVE-2022-41236
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-933x-5g7r-773q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:security-inspector` — affected >=0

## Details
Security Inspector Plugin 117.v6eecc36919c2 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability. This vulnerability allows attackers to replace the generated report stored in a per-session cache and displayed to authorized users at the `…​/report` URL with a report based on attacker-specified report generation options. This could create confusion in users of the plugin who are expecting to see a different result. A security hardening since Jenkins 2.287 and LTS 2.277.2 prevents exploitation of this vulnerability for the _Single user, multiple jobs_ report however, there is no fix at this time. Other report types are still affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41236
- https://github.com/jenkinsci/security-inspector-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2051
