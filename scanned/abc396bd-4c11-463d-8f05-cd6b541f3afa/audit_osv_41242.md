# [M] HedgeDoc: Denial-of-service via YAML alias expansion in note frontmatter

## Summary
Severity: Medium
Advisory: CVE-2026-58486
Aliases: GHSA-qj78-mjch-wwrv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58486
Type: osv

## Details
HedgeDoc is an open source, real-time, collaborative, markdown notes application. Prior to version 1.11.0, HedgeDoc was vulnerable to a YAML alias bomb due to unsafe processing of the note frontmatter. HedgeDoc parsed frontmatter with js-yaml.load (js-yaml v3) via @hedgedoc/meta-marked, which resolved YAML anchor aliases. A compact malicious payload could therefore expand into a huge object structure, consuming excessive CPU. This expansion ran on every request to the publish view (/s/<shortid>) and, when placed under the opengraph key, the editor view (/<noteId>). A ten-level alias bomb could block the single Node.js event loop for roughly 235 seconds per request, causing concurrent requests to hang or drop and rendering the instance unavailable (DoS). Because the note was stored in the database, the impact survived process restarts until the note was removed. toobusy-js did not reliably mitigate the worst cases, as the event loop was saturated before the middleware could respond. This issue was fixed in version 1.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58486.json
- https://github.com/hedgedoc/hedgedoc/security/advisories/GHSA-qj78-mjch-wwrv
- https://nvd.nist.gov/vuln/detail/CVE-2026-58486
- https://github.com/hedgedoc/hedgedoc/commit/c489497e451887bfe400434c5a010940051e9890
