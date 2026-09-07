# [C] OS Command Injection in node-opencv

## Summary
Severity: Critical
Advisory: GHSA-mc7w-4cjf-c973
CVE: CVE-2019-10061
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-mc7w-4cjf-c973
Type: github-advisory

## Affected
- npm: `opencv` — affected >=0 <6.1.0

## Details
utils/find-opencv.js in node-opencv (aka OpenCV bindings for Node.js) prior to 6.1.0 is vulnerable to Command Injection. It does not validate user input allowing attackers to execute arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10061
- https://github.com/peterbraden/node-opencv/commit/81a4b8620188e89f7e4fc985f3c89b58d4bcc86b
- https://github.com/peterbraden/node-opencv/commit/aaece6921d7368577511f06c94c99dd4e9653563
- https://github.com/peterbraden/node-opencv
- https://www.npmjs.com/advisories/789
- https://www.npmjs.com/package/opencv
