# [M] Prototype Pollution in jointjs

## Summary
Severity: Medium
Advisory: GHSA-f3pp-32qc-36w4
CVE: CVE-2021-23444
CWE: CWE-1321, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-f3pp-32qc-36w4
Type: github-advisory

## Affected
- npm: `jointjs` — affected >=0 <3.4.2

## Details
This affects the package jointjs before 3.4.2. A type confusion vulnerability can lead to a bypass of CVE-2020-28480 when the user-provided keys used in the path parameter are arrays in the setByPath function.

## References
- https://github.com/clientIO/joint/pull/1514
- https://github.com/clientIO/joint/commit/e5bf89efef6d5ea572d66870ffd86560de7830a8
- https://github.com/clientIO/joint
- https://github.com/clientIO/joint/releases/tag/v3.4.2
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1655817
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1655816
- https://snyk.io/vuln/SNYK-JS-JOINTJS-1579578
