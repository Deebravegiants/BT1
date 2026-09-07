# [C] OS Command Injection in docker-compose-remote-api

## Summary
Severity: Critical
Advisory: GHSA-q6pj-jh94-5fpr
CVE: CVE-2020-7606
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-q6pj-jh94-5fpr
Type: github-advisory

## Affected
- npm: `docker-compose-remote-api` — affected >=0

## Details
docker-compose-remote-api through 0.1.4 allows execution of arbitrary commands. Within `index.js` of the package, the function `exec(serviceName, cmd, fnStdout, fnStderr, fnExit)` uses the variable `serviceName` which can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7606
- https://snyk.io/vuln/SNYK-JS-DOCKERCOMPOSEREMOTEAPI-560125
