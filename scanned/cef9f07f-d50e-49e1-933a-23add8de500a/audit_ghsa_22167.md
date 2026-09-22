# [M] Missing permission checks in Jenkins CloudBees AWS Credentials Plugin allows enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-jwr9-h4jm-c9ch
CVE: CVE-2021-21625
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jwr9-h4jm-c9ch
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aws-credentials` — affected >=0 <1.28.1

## Details
CloudBees AWS Credentials Plugin 1.28 and earlier does not perform a permission check in a helper method for HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate credentials IDs of AWS credentials stored in Jenkins if any of the following plugins are installed:

- [Amazon Elastic Container Service (ECS) / Fargate](https://plugins.jenkins.io/amazon-ecs)
- [AWS Parameter Store Build Wrapper](https://plugins.jenkins.io/aws-parameter-store)
- [AWS SAM](https://plugins.jenkins.io/aws-sam)\n\nFurther plugins may use this helper method as well without performing a permission check themselves.

Credentials IDs obtained this way can be used as part of an attack to capture the credentials using another vulnerability.

CloudBees AWS Credentials Plugin 1.28.1 performs permission checks in the helper method for HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21625
- https://github.com/jenkinsci/aws-credentials-plugin/commit/dd477a071bd633d9118c63dc3f19a2fd0590aecb
- https://github.com/jenkinsci/aws-credentials-plugin
- https://www.jenkins.io/security/advisory/2021-03-18/#SECURITY-2032
- http://www.openwall.com/lists/oss-security/2021/03/18/5
