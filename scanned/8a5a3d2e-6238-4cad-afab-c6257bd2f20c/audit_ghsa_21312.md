# [H] react-native-reanimated vulnerable to ReDoS

## Summary
Severity: High
Advisory: GHSA-2j79-8pqc-r7x6
CVE: CVE-2022-24373
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-2j79-8pqc-r7x6
Type: github-advisory

## Affected
- npm: `react-native-reanimated` — affected >=0 <2.10.0

## Details
The package react-native-reanimated before 2.10.0 is vulnerable to Regular Expression Denial of Service (ReDoS) due to improper usage of regular expression in the parser of Colors.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24373
- https://github.com/software-mansion/react-native-reanimated/pull/3382
- https://github.com/software-mansion/react-native-reanimated/pull/3382/commits/7adf06d0c59382d884a04be86a96eede3d0432fa
- https://github.com/software-mansion/react-native-reanimated/commit/8a927904366fa2d02df7a11553f8b0aa93471279
- https://github.com/software-mansion/react-native-reanimated
- https://github.com/software-mansion/react-native-reanimated/compare/2.9.1...2.10.0
- https://github.com/software-mansion/react-native-reanimated/releases/tag/3.0.0-rc.1
- https://security.snyk.io/vuln/SNYK-JS-REACTNATIVEREANIMATED-2949507
