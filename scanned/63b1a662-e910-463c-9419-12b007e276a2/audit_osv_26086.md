# [M] CVE-2023-50772

## Summary
Severity: Medium
Advisory: CVE-2023-50772
Aliases: GHSA-wjr6-v4c7-8cv6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-50772
Type: osv

## Details
Jenkins Dingding JSON Pusher Plugin 2.0 and earlier stores access tokens unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3184
- http://www.openwall.com/lists/oss-security/2023/12/13/4
