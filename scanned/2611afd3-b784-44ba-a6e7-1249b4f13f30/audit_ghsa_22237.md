# [M] Credentials stored in plain text by Jenkins White Source Plugin

## Summary
Severity: Medium
Advisory: GHSA-v8v2-fhgv-3vq2
CVE: CVE-2020-2213
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v8v2-fhgv-3vq2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:whitesource` — affected >=0 <20.8.1

## Details
White Source Plugin prior to version 20.8.1 stores credentials in plain text as part of its global configuration file `org.whitesource.jenkins.pipeline.WhiteSourcePipelineStep.xml` and job config.xml files on the Jenkins controller. These credentials could be viewed by users with Extended Read permission (in the case of job config.xml files) or access to the Jenkins controller file system. Version 20.8.1 contains a patch for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2213
- https://github.com/jenkinsci/whitesource-plugin/commit/4a9ee37246848c65cd41c5cf17d84992ffc6d21d
- https://github.com/jenkinsci/whitesource-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1630
- http://www.openwall.com/lists/oss-security/2020/07/02/7
