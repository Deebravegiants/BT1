# [M] Jenkins Folders Plugin information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-36hq-v2fc-rpqp
CVE: CVE-2023-40338
CWE: CWE-209, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-36hq-v2fc-rpqp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-folder` — affected >=0 <6.848.ve3b

## Details
Jenkins Folders Plugin displays an error message when attempting to access the Scan Organization Folder Log if no logs are available.

In Folders Plugin 6.846.v23698686f0f6 and earlier, this error message includes the absolute path of a log file, exposing information about the Jenkins controller file system.

Folders Plugin 6.848.ve3b_fd7839a_81 does not display the absolute path of a log file in the error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40338
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3109
- http://www.openwall.com/lists/oss-security/2023/08/16/3
