# [H] Prototype Pollution in Dexie

## Summary
Severity: High
Advisory: GHSA-3xgx-r9j4-qw9w
CVE: CVE-2022-21189
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-3xgx-r9j4-qw9w
Type: github-advisory

## Affected
- npm: `dexie` — affected >=0 <3.2.2
- npm: `dexie` — affected >=4.0.0-alpha.1 <4.0.0-alpha.3

## Details
Dexie is a minimalistic wrapper for IndexedDB. The package dexie before 3.2.2, from 4.0.0-alpha.1 and before 4.0.0-alpha.3 are vulnerable to Prototype Pollution in the Dexie.setByKeyPath(obj, keyPath, value) function which does not properly check the keys being set (like __proto__ or constructor). This can allow an attacker to add/modify properties of the Object.prototype leading to prototype pollution vulnerability. **Note:** This vulnerability can occur in multiple ways, for example when modifying a collection with untrusted user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21189
- https://github.com/dexie/Dexie.js/commit/1d655a69b9f28c3af6fae10cf5c61df387dc689b
- https://github.com/dexie/Dexie.js
- https://github.com/dexie/Dexie.js/blob/fe682ef24568278c3b31d9d6c93de095d4b77ae8/src/functions/utils.ts%23L134-L164
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2805308
- https://snyk.io/vuln/SNYK-JS-DEXIE-2607042
