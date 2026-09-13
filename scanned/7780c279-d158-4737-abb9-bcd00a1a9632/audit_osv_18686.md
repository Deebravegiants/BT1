# [C] CVE-2020-35458

## Summary
Severity: Critical
Advisory: CVE-2020-35458
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/CVE-2020-35458
Type: osv

## Details
An issue was discovered in ClusterLabs Hawk 2.x through 2.3.0-x. There is a Ruby shell code injection issue via the hawk_remember_me_id parameter in the login_from_cookie cookie. The user logout routine could be used by unauthenticated remote attackers to execute code as hauser.

## References
- https://github.com/ClusterLabs/hawk/releases
- http://www.openwall.com/lists/oss-security/2021/01/12/3
- https://bugzilla.suse.com/show_bug.cgi?id=1179998
- https://www.openwall.com/lists/oss-security/2021/01/12/3
