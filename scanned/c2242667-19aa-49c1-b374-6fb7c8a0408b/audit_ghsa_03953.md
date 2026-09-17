# [H] herbivore downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-7r2x-3qcm-8vfw
CVE: CVE-2016-10665
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-7r2x-3qcm-8vfw
Type: github-advisory

## Affected
- npm: `herbivore` — affected >=0

## Details
Affected versions of `herbivore` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `herbivore`.


## Recommendation

The module author has rewritten much of the package, and in that process, patched the vulnerability, but has not published any of the new code to npm.  

In order to get an updated version, it is necessary to install the package from github. This can be done using the following command:
```
npm i samatt/herbivore
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10665
- https://github.com/samatt/Herbivore/commit/0a041defc3463e99948e5d2064aef54b2128c5a3
- https://github.com/advisories/GHSA-7r2x-3qcm-8vfw
- https://github.com/samatt/herbivore
- https://www.npmjs.com/advisories/258
