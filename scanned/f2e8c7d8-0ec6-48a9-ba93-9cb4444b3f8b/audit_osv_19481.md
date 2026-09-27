# [C] CVE-2021-21388

## Summary
Severity: Critical
Advisory: CVE-2021-21388
Aliases: GHSA-jff2-qjw8-5476
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-21388
Type: osv

## Details
systeminformation is an open source system and OS information library for node.js. A command injection vulnerability has been discovered in versions of systeminformation prior to 5.6.4. The issue has been fixed with a parameter check on user input. Please upgrade to version >= 5.6.4. If you cannot upgrade, be sure to check or sanitize service parameters that are passed to si.inetLatency(), si.inetChecksite(), si.services(), si.processLoad() and other commands. Only allow strings, reject any arrays. String sanitation works as expected.

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-jff2-qjw8-5476
- https://www.npmjs.com/package/systeminformation
- https://github.com/sebhildebrandt/systeminformation/commit/01ef56cd5824ed6da1c11b37013a027fdef67524
- https://github.com/sebhildebrandt/systeminformation/commit/0be6fcd575c05687d1076d5cd6d75af2ebae5a46
- https://github.com/sebhildebrandt/systeminformation/commit/7922366d707de7f20995fc8e30ac3153636bf35f
