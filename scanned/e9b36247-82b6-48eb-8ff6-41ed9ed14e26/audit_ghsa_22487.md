# [H] Arbitrary shell command execution in Jenkins EC2 Plugin

## Summary
Severity: High
Advisory: GHSA-wp79-cpv2-9g7m
CVE: CVE-2017-1000502
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wp79-cpv2-9g7m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2` — affected >=0 <1.38

## Details
Users with permission to create or configure agents in Jenkins 1.37 and earlier could configure an EC2 agent to run arbitrary shell commands on the master node whenever the agent was supposed to be launched. Configuration of these agents now requires the 'Run Scripts' permission typically only granted to administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000502
- https://jenkins.io/security/advisory/2017-12-06
