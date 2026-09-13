# [C] CVE-2021-23470

## Summary
Severity: Critical
Advisory: CVE-2021-23470
Aliases: GHSA-4g77-cvgw-grvw, SNYK-JS-PUTILMERGE-2391487
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2021-23470
Type: osv

## Details
This affects the package putil-merge before 3.8.0. The merge() function does not check the values passed into the argument. An attacker can supply a malicious value by adjusting the value to include the constructor property. Note: This vulnerability derives from an incomplete fix in https://security.snyk.io/vuln/SNYK-JS-PUTILMERGE-1317077

## References
- https://github.com/panates/putil-merge/commit/476d00078dfb2827d7c9ee0f2392c81b864f7bc5
- https://snyk.io/vuln/SNYK-JS-PUTILMERGE-2391487
