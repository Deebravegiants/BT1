# [M] Link Following in Jenkins Pipeline Multibranch Plugin

## Summary
Severity: Medium
Advisory: GHSA-2m9w-9xh2-wxc3
CVE: CVE-2022-25179
CWE: CWE-59
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-2m9w-9xh2-wxc3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-multibranch` — affected >=2.24 <2.26.1
- Maven: `org.jenkins-ci.plugins.workflow:workflow-multibranch` — affected >=0 <2.23.1
- Maven: `org.jenkins-ci.plugins.workflow:workflow-multibranch` — affected >=696.v52535c46f4c9 <696.698.v9b4218eea50f
- Maven: `org.jenkins-ci.plugins.workflow:workflow-multibranch` — affected >=706.vd43c65dec013 <707.v71c3f0a

## Details
Jenkins Pipeline: Multibranch Plugin prior to 2.23.1, 2.26.1, 696.698.v9b4218eea50f, and 707.v71c3f0a_6ccdb_ follows symbolic links to locations outside of the checkout directory for the configured SCM when reading files using the readTrusted step, allowing attackers able to configure Pipelines permission to read arbitrary files on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25179
- https://github.com/CVEProject/cvelist/blob/00bfb5abeecc9f553a2f42954ee540e493498ee9/2022/25xxx/CVE-2022-25179.json
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2613
