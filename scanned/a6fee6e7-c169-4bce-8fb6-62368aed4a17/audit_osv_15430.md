# [C] CVE-2019-16184

## Summary
Severity: Critical
Advisory: CVE-2019-16184
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-16184
Type: osv

## Details
A CSV injection vulnerability was found in Limesurvey before 3.17.14 that allows survey participants to inject commands via their survey responses that will be included in the export CSV file.

## References
- https://www.limesurvey.org/limesurvey-updates/2188-limesurvey-3-17-14-build-190902-released
- https://github.com/LimeSurvey/LimeSurvey/commit/5870fd1037058bc4e43cccf893b576c72293371e#diff-d539f3f8185667ee48db78e1bf65a3b4R46
