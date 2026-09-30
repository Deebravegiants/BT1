# [H] CVE-2018-1999002

## Summary
Severity: High
Advisory: CVE-2018-1999002
Aliases: GHSA-qf38-f2fr-q4x9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999002
Type: osv

## Details
A arbitrary file read vulnerability exists in Jenkins 2.132 and earlier, 2.121.1 and earlier in the Stapler web framework's org/kohsuke/stapler/Stapler.java that allows attackers to send crafted HTTP requests returning the contents of any file on the Jenkins master file system that the Jenkins master has access to.

## References
- https://jenkins.io/security/advisory/2018-07-18/#SECURITY-914
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.exploit-db.com/exploits/46453/
