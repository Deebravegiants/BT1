# [H] CVE-2022-25174

## Summary
Severity: High
Advisory: CVE-2022-25174
Aliases: GHSA-g9fx-6j5c-grmw
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25174
Type: osv

## Details
Jenkins Pipeline: Shared Groovy Libraries Plugin 552.vd9cc05b8a2e1 and earlier uses the same checkout directories for distinct SCMs for Pipeline libraries, allowing attackers with Item/Configure permission to invoke arbitrary OS commands on the controller through crafted SCM contents.

## References
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2463
