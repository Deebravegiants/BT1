# [C] OS command injection in aws-lambda

## Summary
Severity: Critical
Advisory: GHSA-934x-72xh-5hrg
CVE: CVE-2019-10777
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-14
Source: https://github.com/advisories/GHSA-934x-72xh-5hrg
Type: github-advisory

## Affected
- npm: `aws-lambda` — affected >=0 <1.0.5

## Details
In aws-lambda versions prior to version 1.0.5, the "config.FunctioName" is used to construct the argument used within the "exec" function without any sanitization. It is possible for a user to inject arbitrary commands to the "zipCmd" used within "config.FunctionName".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10777
- https://github.com/awspilot/cli-lambda-deploy
- https://snyk.io/vuln/SNYK-JS-AWSLAMBDA-540839
