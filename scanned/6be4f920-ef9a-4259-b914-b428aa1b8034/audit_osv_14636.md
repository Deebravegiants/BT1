# [M] CVE-2019-10378

## Summary
Severity: Medium
Advisory: CVE-2019-10378
Aliases: GHSA-qcfr-65hf-f98x
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2019-10378
Type: osv

## Details
Jenkins TestLink Plugin 3.16 and earlier stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/08/07/1
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1428
- https://www.zerodayinitiative.com/advisories/ZDI-19-839/
