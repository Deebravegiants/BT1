# [H] Arbitrary file write vulnerability in Jenkins Pipeline: Input Step Plugin

## Summary
Severity: High
Advisory: GHSA-29q6-p2cg-4v23
CVE: CVE-2022-34177
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-29q6-p2cg-4v23
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-input-step` — affected >=0 <449.v77f0e8b

## Details
Pipeline: Input Step Plugin 448.v37cea_9a_10a_70 and earlier allows Pipeline authors to specify `file` parameters for Pipeline `input` steps even though they are unsupported. Although the uploaded file is not copied to the workspace, Jenkins archives the file on the controller as part of build metadata using the parameter name without sanitization as a relative path inside a build-related directory.

This allows attackers able to configure Pipelines to create or replace arbitrary files on the Jenkins controller file system with attacker-specified content.

Pipeline: Input Step Plugin 449.v77f0e8b_845c4 prohibits use of `file` parameters for Pipeline `input` steps. Attempts to use them will fail Pipeline execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34177
- https://github.com/jenkinsci/pipeline-input-step-plugin/commit/77f0e8b845c4ad429f6c717eab21cf4e7a69168e
- https://github.com/jenkinsci/pipeline-input-step-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2705
