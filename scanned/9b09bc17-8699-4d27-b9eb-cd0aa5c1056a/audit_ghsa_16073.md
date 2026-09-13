# [H] Regular Expression Denial of Service (ReDoS) in cross-spawn

## Summary
Severity: High
Advisory: GHSA-3xgq-45jj-v275
CVE: CVE-2024-21538
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-08
Source: https://github.com/advisories/GHSA-3xgq-45jj-v275
Type: github-advisory

## Affected
- npm: `cross-spawn` — affected >=7.0.0 <7.0.5
- npm: `cross-spawn` — affected >=0 <6.0.6

## Details
Versions of the package cross-spawn before 7.0.5 are vulnerable to Regular Expression Denial of Service (ReDoS) due to improper input sanitization. An attacker can increase the CPU usage and crash the program by crafting a very large and well crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21538
- https://github.com/moxystudio/node-cross-spawn/issues/165
- https://github.com/moxystudio/node-cross-spawn/pull/160
- https://github.com/moxystudio/node-cross-spawn/commit/5ff3a07d9add449021d806e45c4168203aa833ff
- https://github.com/moxystudio/node-cross-spawn/commit/640d391fde65388548601d95abedccc12943374f
- https://github.com/moxystudio/node-cross-spawn/commit/d35c865b877d2f9ded7c1ed87521c2fdb689c8dd
- https://github.com/moxystudio/node-cross-spawn
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-8366349
- https://security.snyk.io/vuln/SNYK-JS-CROSSSPAWN-8303230
