# [M] CVE-2022-25176

## Summary
Severity: Medium
Advisory: CVE-2022-25176
Aliases: GHSA-6473-gqrj-4p65
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25176
Type: osv

## Details
Jenkins Pipeline: Groovy Plugin 2648.va9433432b33c and earlier follows symbolic links to locations outside of the checkout directory for the configured SCM when reading the script file (typically Jenkinsfile) for Pipelines, allowing attackers able to configure Pipelines to read arbitrary files on the Jenkins controller file system.

## References
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2613
