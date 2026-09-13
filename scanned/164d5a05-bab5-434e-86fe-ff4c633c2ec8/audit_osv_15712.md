# [C] CVE-2019-19010

## Summary
Severity: Critical
Advisory: CVE-2019-19010
Aliases: GHSA-6g88-vr3v-76mf, PYSEC-2019-102
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-16
Source: https://osv.dev/vulnerability/CVE-2019-19010
Type: osv

## Details
Eval injection in the Math plugin of Limnoria (before 2019.11.09) and Supybot (through 2018-05-09) allows remote unprivileged attackers to disclose information or possibly have unspecified other impact via the calc and icalc IRC commands.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/54CQM2TEXRADLE77VOMCPHL5PBHR3ZWJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5P2AGND54UIJV3WHOYO2YINIXSDGAAPO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DRNOUHFEN75QAIKT4Y3HDN3TT5LSIWN2/
- https://github.com/ProgVal/Limnoria/commit/3848ae78de45b35c029cc333963d436b9d2f0a35
- https://github.com/ProgVal/Limnoria/wiki/math-eval-vulnerability
