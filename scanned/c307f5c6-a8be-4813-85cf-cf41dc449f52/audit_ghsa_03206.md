# [M] Regular Expression Denial of Service in postcss

## Summary
Severity: Medium
Advisory: GHSA-hwj9-h5mp-3pm3
CVE: CVE-2021-23368
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-hwj9-h5mp-3pm3
Type: github-advisory

## Affected
- npm: `postcss` — affected >=7.0.0 <7.0.36
- npm: `postcss` — affected >=8.0.0 <8.2.10

## Details
The npm package `postcss` from 7.0.0 and before versions 7.0.36 and 8.2.10 is vulnerable to Regular Expression Denial of Service (ReDoS) during source map parsing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23368
- https://github.com/postcss/postcss/commit/54cbf3c4847eb0fb1501b9d2337465439e849734
- https://github.com/postcss/postcss/commit/8682b1e4e328432ba692bed52326e84439cec9e4
- https://github.com/postcss/postcss/commit/b6f3e4d5a8d7504d553267f80384373af3a3dec5
- https://lists.apache.org/thread.html/r00158f5d770d75d0655c5eef1bdbc6150531606c8f8bcb778f0627be@%3Cdev.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/r16e295b4f02d81b79981237d602cb0b9e59709bafaa73ac98be7cef1@%3Cdev.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/r49afb49b38748897211b1f89c3a64dc27f9049474322b05715695aab@%3Cdev.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/r5acd89f3827ad9a9cad6d24ed93e377f7114867cd98cfba616c6e013@%3Ccommits.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/r8def971a66cf3e375178fbee752e1b04a812a047cc478ad292007e33@%3Cdev.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/rad5af2044afb51668b1008b389ac815a28ecea9eb75ae2cab5a00ebb@%3Ccommits.myfaces.apache.org%3E
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1244795
- https://snyk.io/vuln/SNYK-JS-POSTCSS-1090595
