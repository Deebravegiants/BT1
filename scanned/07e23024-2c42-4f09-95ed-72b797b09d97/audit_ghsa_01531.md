# [M] Sensitive information exposure through logs in npm-registry-fetch

## Summary
Severity: Medium
Advisory: GHSA-jmqm-f2gx-4fjv
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-jmqm-f2gx-4fjv
Type: github-advisory

## Affected
- npm: `npm-registry-fetch` — affected >=0 <4.0.5
- npm: `npm-registry-fetch` — affected >=5.0.0 <8.1.1

## Details
Affected versions of `npm-registry-fetch` are vulnerable to an information exposure vulnerability through log files. The cli supports URLs like `<protocol>://[<user>[:<password>]@]<hostname>[:<port>][:][/]<path>`. The password value is not redacted and is printed to stdout and also to any generated log files.

## References
- https://github.com/npm/npm-registry-fetch/security/advisories/GHSA-jmqm-f2gx-4fjv
- https://github.com/npm/npm-registry-fetch/pull/29
- https://github.com/npm/npm-registry-fetch/commit/18bf9b97fb1deecdba01ffb05580370846255c88
- https://github.com/npm/npm-registry-fetch
- https://snyk.io/vuln/SNYK-JS-NPMREGISTRYFETCH-575432
