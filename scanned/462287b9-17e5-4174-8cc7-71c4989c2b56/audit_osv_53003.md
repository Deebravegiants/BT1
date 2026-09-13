# [H] CVE-2022-25844

## Summary
Severity: High
Advisory: CVE-2022-25844
Aliases: GHSA-m2h2-264f-f486
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-01
Source: https://osv.dev/vulnerability/CVE-2022-25844
Type: osv

## Details
The package angular after 1.7.0 are vulnerable to Regular Expression Denial of Service (ReDoS) by providing a custom locale rule that makes it possible to assign the parameter in posPre: ' '.repeat() of NUMBER_FORMATS.PATTERNS[1].posPre with a very high value. **Note:** 1) This package has been deprecated and is no longer maintained. 2) The vulnerable versions are 1.7.0 and higher.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2WUSPYOTOMAZPDEFPWPSCSPMNODRDKK3/
- https://lists.debian.org/debian-lts-announce/2025/07/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7LNAKCNTVBIHWAUT3FKWV5N67PQXSZOO/
- https://security.netapp.com/advisory/ntap-20220629-0009/
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-2772736
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBANGULAR-2772738
- https://snyk.io/vuln/SNYK-JS-ANGULAR-2772735
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2772737
- https://stackblitz.com/edit/angularjs-material-blank-zvtdvb
