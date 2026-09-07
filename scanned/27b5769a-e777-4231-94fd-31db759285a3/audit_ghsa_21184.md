# [M] Jenkins Job Configuration History Plugin does not require POST requests for several HTTP endpoints

## Summary
Severity: Medium
Advisory: GHSA-j896-j72w-cr32
CVE: CVE-2022-36887
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-j896-j72w-cr32
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jobConfigHistory` — affected >=0 <1156.v536a_97b_8d649

## Details
Jenkins Job Configuration History Plugin 1155.v28a_46a_cc06a_5 and earlier does not require POST requests for several HTTP endpoints, resulting in cross-site request forgery (CSRF) vulnerabilities.

These vulnerabilities allow attackers to delete entries from job, agent, and system configuration history, or restore older versions of job, agent, and system configurations.

Job Configuration History Plugin 1156.v536a_97b_8d649 requires POST requests for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36887
- https://github.com/jenkinsci/job-config-history-plugin/commit/536a97b8d649b3114f5db24ea32a7c63188a35c6
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2766
- http://www.openwall.com/lists/oss-security/2022/07/27/1
