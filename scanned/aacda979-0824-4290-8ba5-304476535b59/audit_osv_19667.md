# [M] CVE-2021-23472

## Summary
Severity: Medium
Advisory: CVE-2021-23472
Aliases: GHSA-mw6q-98mp-g8g8
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2021-23472
Type: osv

## Details
This affects versions before 1.19.1 of package bootstrap-table. A type confusion vulnerability can lead to a bypass of input sanitization when the input provided to the escapeHTML function is an array (instead of a string) even if the escape attribute is set.

## References
- https://github.com/wenzhixin/bootstrap-table/blob/develop/src/utils/index.js%23L218
- https://security.snyk.io/vuln/SNYK-JS-BOOTSTRAPTABLE-1657597
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1910690
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1910689
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBWENZHIXIN-1910687
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1910688
- https://snyk.io/vuln/SNYK-JS-BOOTSTRAPTABLE-1657597
