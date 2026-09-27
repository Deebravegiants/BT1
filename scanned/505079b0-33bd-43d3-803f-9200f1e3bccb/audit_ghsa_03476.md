# [M] OS Command Injection in rpi

## Summary
Severity: Medium
Advisory: GHSA-vf26-7gjf-f92r
CVE: CVE-2019-10796
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-vf26-7gjf-f92r
Type: github-advisory

## Affected
- npm: `rpi` — affected >=0

## Details
rpi through 0.0.3 allows execution of arbritary commands. The variable pinNumbver in function GPIO within src/lib/gpio.js is used as part of the arguement of exec function without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10796
- https://github.com/xseignard/rpi/blob/master/src/lib/gpio.js#L47
- https://snyk.io/vuln/SNYK-JS-RPI-548942
