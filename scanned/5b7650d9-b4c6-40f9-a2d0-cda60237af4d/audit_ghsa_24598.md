# [M] Jenkins Gitlab Hook Plugin stores and displays GitLab API token in plain text

## Summary
Severity: Medium
Advisory: GHSA-7p4p-v6hr-gp3m
CVE: CVE-2018-1000196
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7p4p-v6hr-gp3m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.ruby-plugins:gitlab-hook` — affected >=0

## Details
A exposure of sensitive information vulnerability exists in Jenkins Gitlab Hook Plugin 1.4.2 and older in gitlab_notifier.rb, views/gitlab_notifier/global.erb that allows attackers with local Jenkins master file system access or control of a Jenkins administrator's web browser (e.g. malicious extension) to retrieve the configured Gitlab token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000196
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-263
