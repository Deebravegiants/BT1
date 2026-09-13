# [H] OS command execution vulnerability in Perfecto Plugin

## Summary
Severity: High
Advisory: GHSA-jq84-6fmm-6qv6
CVE: CVE-2020-2261
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jq84-6fmm-6qv6
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:perfecto` — affected >=0 <1.18

## Details
Perfecto Plugin allows specifying Perfecto Connect Path and Perfecto Connect File Name in job configurations.

This command is executed on the Jenkins controller in Perfecto Plugin 1.17 and earlier, allowing attackers with Job/Configure permission to run arbitrary commands on the Jenkins controller.

Perfecto Plugin 1.18 executes the specified commands on the agent the build is running on.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2261
- https://github.com/jenkinsci/perfecto-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1980
- http://www.openwall.com/lists/oss-security/2020/09/16/3
