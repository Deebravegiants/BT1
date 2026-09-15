# [M] Rocket.Chat: Missing URL protocol sanitization in ImageElement allows javascript: URLs in markdown images

## Summary
Severity: Medium
Advisory: CVE-2026-47733
Aliases: GHSA-vvrf-fq54-q4pr
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-47733
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.0, the ImageElement component in packages/gazzodown renders user-controlled src values directly into <a href> and <img src> attributes without protocol sanitization. Unlike the analogous LinkSpan component — which uses sanitizeUrl to block javascript:, data:, and vbscript: protocols — ImageElement passes the raw URL through unchanged. An authenticated user can post a markdown image with a javascript: URL that, if clicked on an older browser, would execute arbitrary JavaScript in the viewer's session. This vulnerability is fixed in 8.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47733.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-vvrf-fq54-q4pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-47733
