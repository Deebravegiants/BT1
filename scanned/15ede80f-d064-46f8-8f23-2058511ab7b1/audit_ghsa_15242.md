# [H] Arbitrary file read vulnerability in Git server Plugin can lead to RCE

## Summary
Severity: High
Advisory: GHSA-vph5-2q33-7r9h
CVE: CVE-2024-23899
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-vph5-2q33-7r9h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git-server` — affected >=0 <99.101.v720e86326c09

## Details
Jenkins Git server Plugin uses the [args4j](https://github.com/kohsuke/args4j) library to parse command arguments and options on the Jenkins controller when processing Git commands received via SSH. This command parser has a feature that replaces an @ character followed by a file path in an argument with the file’s contents (`expandAtFiles`). This feature is enabled by default and Git server Plugin 99.va_0826a_b_cdfa_d and earlier does not disable it.

This allows attackers with Overall/Read permission to read the first two lines of arbitrary files on the Jenkins controller file system using the default character encoding of the Jenkins controller process.

See [SECURITY-3314](https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3314) for further information about the potential impact of being able to read files on the Jenkins controller, as well as the [limitations for reading binary files](https://www.jenkins.io/security/advisory/2024-01-24/#binary-files-note). Note that for this issue, unlike SECURITY-3314, attackers need Overall/Read permission.

## Fix Description
Git server Plugin 99.101.v720e86326c09 disables the command parser feature that replaces an @ character followed by a file path in an argument with the file’s contents for CLI commands.

## Workaround
Navigate to Manage Jenkins » Security and ensure that the SSHD Port setting in the SSH Server section is set to Disable. This disables access to Git repositories hosted by Jenkins (and the Jenkins CLI) via SSH.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23899
- https://github.com/jenkinsci/git-server-plugin/commit/068ac7cc2574882ef9f5a486e001228a71d881ad
- https://github.com/jenkinsci/git-server-plugin
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3319
- http://www.openwall.com/lists/oss-security/2024/01/24/6
