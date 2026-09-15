# [C] OS Command Injection in node-key-sender

## Summary
Severity: Critical
Advisory: GHSA-4xrw-wvmq-8jmh
CVE: CVE-2020-7627
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-4xrw-wvmq-8jmh
Type: github-advisory

## Affected
- npm: `node-key-sender` — affected >=0

## Details
node-key-sender through 1.0.11 is vulnerable to Command Injection. It allows execution of arbitrary commands via the 'arrParams' argument in the 'execute()' function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7627
- https://github.com/garimpeiro-it/node-key-sender/blob/master/key-sender.js#L117
- https://snyk.io/vuln/SNYK-JS-NODEKEYSENDER-564261
