# [M] CVE-2022-25177

## Summary
Severity: Medium
Advisory: CVE-2022-25177
Aliases: GHSA-q234-x887-9rxh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25177
Type: osv

## Details
Jenkins Pipeline: Shared Groovy Libraries Plugin 552.vd9cc05b8a2e1 and earlier follows symbolic links to locations outside of the expected Pipeline library when reading files using the libraryResource step, allowing attackers able to configure Pipelines to read arbitrary files on the Jenkins controller file system.

## References
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2613
