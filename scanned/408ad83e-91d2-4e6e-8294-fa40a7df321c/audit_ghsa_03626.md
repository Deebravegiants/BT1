# [H] Arbitrary File Write in iobroker.js-controller

## Summary
Severity: High
Advisory: GHSA-cmch-296j-wfvw
CVE: CVE-2019-10767
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-cmch-296j-wfvw
Type: github-advisory

## Affected
- npm: `iobroker.js-controller` — affected >=0 <2.0.25

## Details
Versions of `iobroker.controller` prior to 2.0.25 are vulnerable to Path Traversal. The package fails to restrict access to folders outside of the intended `/adapter/<adapter-name>` folder, which may allow attackers to include arbitrary files in the system. An attacker would need to be authenticated to perform the attack but the package has authentication disabled by default.


## Recommendation

Upgrade to version 2.0.25 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10767
- https://github.com/ioBroker/ioBroker.js-controller/commit/f6e292c6750a491a5000d0f851b2fede4f9e2fda
- https://snyk.io/vuln/SNYK-JS-IOBROKERJSCONTROLLER-534881
- https://www.npmjs.com/advisories/1419
