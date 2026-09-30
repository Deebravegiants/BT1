# [M] User input results in Unbounded resource consumption in @zxcvbn-ts/core

## Summary
Severity: Medium
Advisory: CVE-2023-34109
Aliases: GHSA-38hx-x5hq-5fg4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-34109
Type: osv

## Details
zxcvbn-ts is an open source password strength estimator written in typescript. This vulnerability affects users running on the nodeJS platform which are using the second argument of the zxcvbn function. It can result in an unbounded resource consumption as the user inputs array is extended with every function call. Browsers are impacted, too but a single user need to do a lot of input changes so that it affects the browser, while the node process gets the inputs of every user of a platform and can be killed that way. This problem has been patched in version 3.0.2. Users are advised to upgrade. Users unable to upgrade should stop using the second argument of the zxcvbn function and use the zxcvbnOptions.setOptions function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34109.json
- https://github.com/zxcvbn-ts/zxcvbn/security/advisories/GHSA-38hx-x5hq-5fg4
- https://nvd.nist.gov/vuln/detail/CVE-2023-34109
- https://github.com/zxcvbn-ts/zxcvbn/commit/3f9bed21b5d01f6f6863476822ca857355fba22f
