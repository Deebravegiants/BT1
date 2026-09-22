# [H] CVE-2022-30948

## Summary
Severity: High
Advisory: CVE-2022-30948
Aliases: GHSA-5786-3qjg-mr88
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-30948
Type: osv

## Details
Jenkins Mercurial Plugin 2.16 and earlier allows attackers able to configure pipelines to check out some SCM repositories stored on the Jenkins controller's file system using local paths as SCM URLs, obtaining limited information about other projects' SCM contents.

## References
- http://www.openwall.com/lists/oss-security/2022/05/17/8
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2478
