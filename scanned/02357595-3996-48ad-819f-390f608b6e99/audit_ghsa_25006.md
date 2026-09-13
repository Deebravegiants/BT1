# [M] Improper Privilege Management in Jenkins Config File Provider Plugin

## Summary
Severity: Medium
Advisory: GHSA-6h72-m3xw-fp3c
CVE: CVE-2017-1000104
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6h72-m3xw-fp3c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <2.16.2

## Details
The Config File Provider Plugin is used to centrally manage configuration files that often include secrets, such as passwords. Users with only Overall/Read access to Jenkins were able to access URLs directly that allowed viewing these files. Access to view these files now requires sufficient permissions to configure the provided files, view the configuration of the folder in which the configuration files are defined, or have Job/Configure permissions to a job able to use these files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000104
- https://jenkins.io/security/advisory/2017-08-07
