# [C] promise-probe OS command injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-vmqq-7qvx-68qx
CVE: CVE-2019-10791
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vmqq-7qvx-68qx
Type: github-advisory

## Affected
- npm: `promise-probe` — affected >=0 <0.1.10

## Details
promise-probe before 0.10.0 allows remote attackers to perform a command injection attack. The `file`, `outputFile` and `options` functions can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10791
- https://github.com/dottgonzo/node-promise-probe/commit/0d9affb67fc1ad985903536d35372cf55efe5a45
- https://snyk.io/vuln/SNYK-JS-PROMISEPROBE-546816
