# [C] Arbitrary file read vulnerability through the Jenkins CLI can lead to RCE

## Summary
Severity: Critical
Advisory: GHSA-6f9g-cxwr-q5jr
CVE: CVE-2024-23897
CWE: CWE-22, CWE-27
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-6f9g-cxwr-q5jr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.606 <2.426.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.427 <2.440.1
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.441 <2.442

## Details
Jenkins has a built-in command line interface (CLI) to access Jenkins from a script or shell environment.

Jenkins uses the args4j library to parse command arguments and options on the Jenkins controller when processing CLI commands. This command parser has a feature that replaces an @ character followed by a file path in an argument with the file’s contents (expandAtFiles). This feature is enabled by default and Jenkins 2.441 and earlier, LTS 2.426.2 and earlier does not disable it.

This allows attackers to read arbitrary files on the Jenkins controller file system using the default character encoding of the Jenkins controller process.

* Attackers with Overall/Read permission can read entire files.

* Attackers without Overall/Read permission can read the first few lines of files. The number of lines that can be read depends on available CLI commands. As of publication of this advisory, the Jenkins security team has found ways to read the first three lines of files in recent releases of Jenkins without having any plugins installed, and has not identified any plugins that would increase this line count.

Binary files containing cryptographic keys used for various Jenkins features can also be read, with some limitations (see note on binary files below). As of publication, the Jenkins security team has confirmed the following possible attacks in addition to reading contents of all files with a known file path. All of them leverage attackers' ability to obtain cryptographic keys from binary files, and are therefore only applicable to instances where that is feasible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23897
- https://github.com/jenkinsci/jenkins/commit/554f03782057c499c49bbb06575f0d28b5200edb
- https://github.com/jenkinsci/jenkins
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-23897
- https://www.jenkins.io/changelog-stable/#v2.440.1
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3314
- https://www.sonarsource.com/blog/excessive-expansion-uncovering-critical-security-vulnerabilities-in-jenkins
- https://www.vicarius.io/vsociety/posts/the-anatomy-of-a-jenkins-vulnerability-cve-2024-23897-revealed-1
- http://packetstormsecurity.com/files/176839/Jenkins-2.441-LTS-2.426.3-CVE-2024-23897-Scanner.html
- http://packetstormsecurity.com/files/176840/Jenkins-2.441-LTS-2.426.3-Arbitrary-File-Read.html
- http://www.openwall.com/lists/oss-security/2024/01/24/6
