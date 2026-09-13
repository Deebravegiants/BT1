# [H] CVE-2022-25173

## Summary
Severity: High
Advisory: CVE-2022-25173
Aliases: GHSA-4m7p-55jm-3vwv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25173
Type: osv

## Details
Jenkins Pipeline: Groovy Plugin 2648.va9433432b33c and earlier uses the same checkout directories for distinct SCMs when reading the script file (typically Jenkinsfile) for Pipelines, allowing attackers with Item/Configure permission to invoke arbitrary OS commands on the controller through crafted SCM contents.

## References
- http://www.openwall.com/lists/oss-security/2022/02/15/2
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2463
