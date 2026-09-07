# [C] conf-cfg-ini Prototype Pollution via malicious INI file before v1.2.2

## Summary
Severity: Critical
Advisory: GHSA-m6mg-jvjf-w44x
CVE: CVE-2020-28441
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-m6mg-jvjf-w44x
Type: github-advisory

## Affected
- npm: `conf-cfg-ini` — affected >=0 <1.2.2

## Details
This affects the package conf-cfg-ini before 1.2.2. If an attacker submits a malicious INI file to an application that parses it with decode, they will pollute the prototype on the application. This can be exploited further depending on the context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28441
- https://github.com/loge5/conf-cfg-ini/commit/3a88a6c52c31eb6c0f033369eed40aa168a636ea
- https://github.com/loge5/conf-cfg-ini/commit/ecd878f8f7398e765739e989c7fe7cc052308947
- https://github.com/loge5/conf-cfg-ini
- https://security.snyk.io/vuln/SNYK-JS-CONFCFGINI-1048973
