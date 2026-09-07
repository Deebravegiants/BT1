# [M] Cross-Site Request Forgery in Jenkins Failed Job Deactivator Plugin

## Summary
Severity: Medium
Advisory: GHSA-cp6q-836q-gmj3
CVE: CVE-2022-34817
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-cp6q-836q-gmj3
Type: github-advisory

## Affected
- Maven: `de.einsundeins.jenkins.plugins.failedjobdeactivator:failedJobDeactivator` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Failed Job Deactivator Plugin 1.2.1 and earlier allows attackers to disable jobs. This CSRF vulnerability is only exploitable in Jenkins 2.286 and earlier, LTS 2.277.1 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.277/#upgrading-to-jenkins-lts-2-277-2).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34817
- https://github.com/jenkinsci/failedjobdeactivator-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2061
