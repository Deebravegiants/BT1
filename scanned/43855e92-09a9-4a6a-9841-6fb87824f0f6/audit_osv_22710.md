# [H] CVE-2022-36883

## Summary
Severity: High
Advisory: CVE-2022-36883
Aliases: GHSA-v878-67xw-grw2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36883
Type: osv

## Details
A missing permission check in Jenkins Git Plugin 4.11.3 and earlier allows unauthenticated attackers to trigger builds of jobs configured to use an attacker-specified Git repository and to cause them to check out an attacker-specified commit.

## References
- http://www.openwall.com/lists/oss-security/2022/07/27/1
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-284
