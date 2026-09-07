# [M] Erxes vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-g9ph-r9hc-34r8
CVE: CVE-2021-32853
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-g9ph-r9hc-34r8
Type: github-advisory

## Affected
- npm: `erxes` — affected >=0

## Details
Erxes, an experience operating system (XOS) with a set of plugins, is vulnerable to cross-site scripting in all versions. This results in client-side code execution. The victim must follow a malicious link or be redirected there from malicious web site. There are no known patches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32853
- https://github.com/erxes/erxes
- https://github.com/erxes/erxes/blob/f131b49add72032650d483f044d00658908aaf4a/widgets/server/index.ts#L54
- https://github.com/erxes/erxes/blob/f131b49add72032650d483f044d00658908aaf4a/widgets/server/views/widget.ejs#L14
- https://securitylab.github.com/advisories/GHSL-2021-103-erxes
