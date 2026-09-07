# [M] External Monitor Job Type Plugin does not require POST requests for an HTTP endpoint

## Summary
Severity: Medium
Advisory: GHSA-6x63-hrxg-2hjx
CVE: CVE-2022-36886
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-6x63-hrxg-2hjx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:external-monitor-job` — affected >=0 <192.ve979ca_8b_3ccd

## Details
Jenkins External Monitor Job Type Plugin 191.v363d0d1efdf8 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to create runs of an external job.

External Monitor Job Type Plugin 192.ve979ca_8b_3ccd requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36886
- https://github.com/jenkinsci/external-monitor-job-plugin/commit/e979ca8b3ccd8cf2b098533e1529d104b6bfd7da
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2762
- http://www.openwall.com/lists/oss-security/2022/07/27/1
