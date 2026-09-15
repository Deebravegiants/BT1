# [M] CVE-2019-16180

## Summary
Severity: Medium
Advisory: CVE-2019-16180
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-16180
Type: osv

## Details
Limesurvey before 3.17.14 allows remote attackers to bruteforce the login form and enumerate usernames when the LDAP authentication method is used.

## References
- https://www.limesurvey.org/limesurvey-updates/2188-limesurvey-3-17-14-build-190902-released
- https://github.com/LimeSurvey/LimeSurvey/commit/5870fd1037058bc4e43cccf893b576c72293371e#diff-d539f3f8185667ee48db78e1bf65a3b4R44
