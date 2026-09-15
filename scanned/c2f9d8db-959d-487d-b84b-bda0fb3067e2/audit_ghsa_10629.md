# [M] Zod jsVideoUrlParser vulnerable to ReDoS in util.js

## Summary
Severity: Medium
Advisory: GHSA-8fgx-wgvr-pcx8
CVE: CVE-2026-5986
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8fgx-wgvr-pcx8
Type: github-advisory

## Affected
- npm: `js-video-url-parser` — affected >=0

## Details
A weakness has been identified in Zod jsVideoUrlParser up to 0.5.1. The impacted element is the function getTime in the library lib/util.js. This manipulation of the argument timestamp causes inefficient regular expression complexity. It is possible to initiate the attack remotely. The exploit has been made available to the public and could be used for attacks. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5986
- https://github.com/Zod-/jsVideoUrlParser/issues/121
- https://github.com/Zod-/jsVideoUrlParser/issues/121#issue-4159661957
- https://github.com/Zod-/jsVideoUrlParser
- https://vuldb.com/submit/791911
- https://vuldb.com/vuln/356540
- https://vuldb.com/vuln/356540/cti
