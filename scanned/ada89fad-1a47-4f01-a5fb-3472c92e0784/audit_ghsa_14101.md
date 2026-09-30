# [M] Jenkins Pipeline Utility Steps Plugin arbitrary file write vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6987-xccv-fhjp
CVE: CVE-2023-32981
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-6987-xccv-fhjp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-utility-steps` — affected >=0 <2.15.3

## Details
Jenkins Pipeline Utility Steps Plugin provides the `untar` and `unzip` Pipeline steps to extract archives into job workspaces.

Pipeline Utility Steps Plugin 2.15.2 and earlier does not validate or limit file paths of files contained within these archives.

This allows attackers able to provide crafted archives as parameters to create or replace arbitrary files on the agent file system with attacker-specified content.

Pipeline Utility Steps Plugin 2.15.3 rejects extraction of files in `tar` and `zip` archives that would be placed outside the expected destination directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32981
- https://github.com/jenkinsci/pipeline-utility-steps-plugin/commit/0ba4f329ee27c023609653e25bdd5604c5e46a11
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2196
