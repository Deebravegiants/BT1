# [H] selenium-binaries downloads resources over HTTP

## Summary
Severity: High
Advisory: GHSA-h4mc-r4f4-hcf4
CVE: CVE-2016-10589
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-h4mc-r4f4-hcf4
Type: github-advisory

## Affected
- npm: `selenium-binaries` — affected >=0 <0.15.0

## Details
Versions of `selenium-binaries` prior to 0.15.0 insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `selenium-binaries`.


## Recommendation

A fix for this vulnerability is available on the `master` branch of the repository as part of version 0.15.0.

Another mitigation currently available is to use an alternate package, such as [selenium-webdriver](https://www.npmjs.com/package/selenium-webdriver), the official selenium bindings for node.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10589
- https://github.com/spunjs/selenium-binaries/pull/33
- https://github.com/spunjs/selenium-binaries/commit/be37e82a3c43a4f1679d66cf9467085ec9994c47
- https://github.com/spunjs/selenium-binaries
- https://www.huntr.dev/bounties/1-npm-selenium-binaries
- https://www.npmjs.com/advisories/175
