# [M] Jenkins Failed Job Deactivator Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hcjr-6jq3-392p
CVE: CVE-2022-34818
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-hcjr-6jq3-392p
Type: github-advisory

## Affected
- Maven: `de.einsundeins.jenkins.plugins.failedjobdeactivator:failedJobDeactivator` — affected >=0

## Details
Jenkins Failed Job Deactivator Plugin 1.2.1 and earlier does not perform permission checks in several views and HTTP endpoints.

This allows attackers with Overall/Read permission to disable jobs.

Additionally, these endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34818
- https://github.com/jenkinsci/failedjobdeactivator-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2061
