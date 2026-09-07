# [H] angular Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-89mq-4x47-5v83
CVE: CVE-2019-10768
CWE: CWE-1321, CWE-20, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-89mq-4x47-5v83
Type: github-advisory

## Affected
- npm: `angular` — affected >=0 <1.7.9

## Details
Versions of `angular ` prior to 1.7.9 are vulnerable to prototype pollution. The deprecated API function `merge()` does not restrict the modification of an Object's prototype in the , which may allow an attacker to add or modify an existing property that will exist on all objects.

## Recommendation

Upgrade to version 1.7.9 or later. The function was already deprecated and upgrades are not expected to break functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10768
- https://github.com/angular/angular.js/pull/16913
- https://github.com/angular/angular.js/commit/add78e62004e80bb1e16ab2dfe224afa8e513bc3
- https://github.com/angular/angular.js
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b%40%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://snyk.io/vuln/SNYK-JS-ANGULAR-534884
