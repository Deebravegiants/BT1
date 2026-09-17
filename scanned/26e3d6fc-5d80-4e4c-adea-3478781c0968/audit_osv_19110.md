# [H] CVE-2020-7752

## Summary
Severity: High
Advisory: CVE-2020-7752
Aliases: GHSA-94xh-2fmc-xf5j, SNYK-JS-SYSTEMINFORMATION-1021909
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-26
Source: https://osv.dev/vulnerability/CVE-2020-7752
Type: osv

## Details
This affects the package systeminformation before 4.27.11. This package is vulnerable to Command Injection. The attacker can concatenate curl's parameters to overwrite Javascript files and then execute any OS commands.

## References
- https://github.com/sebhildebrandt/systeminformation/commit/931fecaec2c1a7dcc10457bb8cd552d08089da61
- https://snyk.io/vuln/SNYK-JS-SYSTEMINFORMATION-1021909
- https://github.com/sebhildebrandt/systeminformation/blob/master/lib/internet.js
