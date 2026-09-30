# [M] OS Command Injection in node-notifier

## Summary
Severity: Medium
Advisory: GHSA-5fw9-fq32-wv5p
CVE: CVE-2020-7789
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-12-21
Source: https://github.com/advisories/GHSA-5fw9-fq32-wv5p
Type: github-advisory

## Affected
- npm: `node-notifier` — affected >=0 <8.0.1

## Details
This affects the package node-notifier before 8.0.1. It allows an attacker to run arbitrary commands on Linux machines due to the options params not being sanitised when being passed an array.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7789
- https://github.com/mikaelbr/node-notifier/commit/5d62799dab88505a709cd032653b2320c5813fce
- https://github.com/mikaelbr/node-notifier/blob/master/lib/utils.js%23L303
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1050371
- https://snyk.io/vuln/SNYK-JS-NODENOTIFIER-1035794
