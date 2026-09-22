# [H] Jenkins Splunk Plugin Sandbox Bypass

## Summary
Severity: High
Advisory: GHSA-cjr8-5rw4-wh65
CVE: CVE-2019-10390
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cjr8-5rw4-wh65
Type: github-advisory

## Affected
- Maven: `com.splunk.splunkins:splunk-devops` — affected >=0 <1.8.0

## Details
Jenkins Splunk Plugin has a form validation HTTP endpoint used to validate a user-submitted Groovy script through compilation, which was not subject to sandbox protection. This allowed attackers with Overall/Read access to execute arbitrary code on the Jenkins controller by applying AST transforming annotations such as `@Grab` to source code elements.

The affected HTTP endpoint now applies a safe Groovy compiler configuration preventing the use of unsafe AST transforming annotations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10390
- https://github.com/jenkinsci/splunk-devops-plugin/commit/58db2878a7faa4c34f73774f28740e5ac8041928
- https://jenkins.io/security/advisory/2019-08-28/#SECURITY-1294
- http://www.openwall.com/lists/oss-security/2019/08/28/4
