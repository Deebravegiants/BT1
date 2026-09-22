# [C] Node-Traceroute RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8j9v-qhp4-wv55
CVE: CVE-2018-21268
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8j9v-qhp4-wv55
Type: github-advisory

## Affected
- npm: `traceroute` — affected >=0

## Details
The traceroute (aka node-traceroute) package through 1.0.0 for Node.js allows remote command injection via the host parameter. This occurs because the `Child.exec()` method, which is considered to be not entirely safe, is used. In particular, an OS command can be placed after a newline character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21268
- https://github.com/jaw187/node-traceroute/commit/b99ee024a01a40d3d20a92ad3769cc78a3f6386f
- https://github.com/jaw187/node-traceroute
- https://github.com/jaw187/node-traceroute/tags
- https://medium.com/@shay_62828/shell-command-injection-through-traceroute-npm-package-a4cf7b6553e3
- https://snyk.io/vuln/npm:traceroute:20160311
- https://www.linkedin.com/posts/op-innovate_shell-command-injection-through-traceroute-activity-6678956453086191616-Rcpy
- https://www.npmjs.com/advisories/1465
- https://www.op-c.net/2020/06/17/shell-command-injection-through-traceroute-npm-package
