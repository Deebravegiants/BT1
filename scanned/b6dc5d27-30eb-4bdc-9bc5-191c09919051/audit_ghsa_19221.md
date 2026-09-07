# [H] Jenkins Health Advisor by CloudBees Plugin Vulnerable to Cross-Site Scripting

## Summary
Severity: High
Advisory: GHSA-xrpq-4g9w-qrwj
CVE: CVE-2025-47885
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-xrpq-4g9w-qrwj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-jenkins-advisor` — affected >=0 <374.376.v3a_41a_a_142efe

## Details
Jenkins Health Advisor by CloudBees Plugin 374.v194b_d4f0c8c8 and earlier does not escape responses from the Jenkins Health Advisor server, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control Jenkins Health Advisor server responses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47885
- https://github.com/jenkinsci/cloudbees-jenkins-advisor-plugin/commit/4b456b3110d1504d7dce8e7fca84c4e8793650e6
- https://github.com/jenkinsci/cloudbees-jenkins-advisor-plugin
- https://www.jenkins.io/security/advisory/2025-05-14/#SECURITY-3559
