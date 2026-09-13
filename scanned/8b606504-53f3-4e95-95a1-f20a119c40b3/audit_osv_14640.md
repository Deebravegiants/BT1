# [H] CVE-2019-10392

## Summary
Severity: High
Advisory: CVE-2019-10392
Aliases: GHSA-hw6x-2qwv-rxr7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-12
Source: https://osv.dev/vulnerability/CVE-2019-10392
Type: osv

## Details
Jenkins Git Client Plugin 2.8.4 and earlier and 3.0.0-rc did not properly restrict values passed as URL argument to an invocation of 'git ls-remote', resulting in OS command injection.

## References
- http://www.openwall.com/lists/oss-security/2019/09/12/2
- https://jenkins.io/security/advisory/2019-09-12/#SECURITY-1534
