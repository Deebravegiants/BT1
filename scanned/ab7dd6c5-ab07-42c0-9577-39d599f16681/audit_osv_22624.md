# [M] CVE-2022-34802

## Summary
Severity: Medium
Advisory: CVE-2022-34802
Aliases: GHSA-pgp9-x83g-v8x8
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-30
Source: https://osv.dev/vulnerability/CVE-2022-34802
Type: osv

## Details
Jenkins RocketChat Notifier Plugin 1.5.2 and earlier stores the login password and webhook token unencrypted in its global configuration file on the Jenkins controller where they can be viewed by users with access to the Jenkins controller file system.

## References
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2088
