# [M] Prototype Pollution in dset

## Summary
Severity: Medium
Advisory: GHSA-23wx-cgxq-vpwx
CVE: CVE-2022-25645
CWE: CWE-1321
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-23wx-cgxq-vpwx
Type: github-advisory

## Affected
- npm: `dset` — affected >=0 <3.1.2
- Maven: `org.webjars.npm:dset` — affected >=0 <3.1.2

## Details
All versions of `dset` prior to 3.1.2 are vulnerable to Prototype Pollution via `dset/merge` mode, as the `dset` function checks for prototype pollution by validating if the top-level path contains `__proto__`, `constructor` or `prototype`. By crafting a malicious object, it is possible to bypass this check and achieve prototype pollution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25645
- https://github.com/lukeed/dset
- https://github.com/lukeed/dset/blob/master/src/merge.js%23L9
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2431974
- https://snyk.io/vuln/SNYK-JS-DSET-2330881
