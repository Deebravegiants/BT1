# [C] OS Command Injection in node-prompt-here

## Summary
Severity: Critical
Advisory: GHSA-f8fh-8rgm-227h
CVE: CVE-2020-7602
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-f8fh-8rgm-227h
Type: github-advisory

## Affected
- npm: `node-prompt-here` — affected >=0

## Details
node-prompt-here through 1.0.1 allows execution of arbitrary commands. The `runCommand()` is called by `getDevices()` function in file `linux/manager.js`, which is required by the `index. process.env.NM_CLI` in the file `linux/manager.js`. This function is used to construct the argument of function `execSync()`, which can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7602
- https://snyk.io/vuln/SNYK-JS-NODEPROMPTHERE-560115
