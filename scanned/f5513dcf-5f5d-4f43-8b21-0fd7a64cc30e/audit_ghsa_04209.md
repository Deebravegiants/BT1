# [M] @steipete/summarize is Vulnerable to Disk Exhaustion via Crafted Media Responses

## Summary
Severity: Medium
Advisory: GHSA-q9xm-f36c-xm3q
CVE: CVE-2026-53781
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-q9xm-f36c-xm3q
Type: github-advisory

## Affected
- npm: `@steipete/summarize-core` — affected >=0 <0.17.0

## Details
Summarize before 0.17.0 contains a resource exhaustion vulnerability that allows remote attackers to cause disk exhaustion by serving media responses that bypass the enforced size limit through missing or misreported Content-Length headers, chunked transfer encoding, or failed HEAD requests. Attackers who control a podcast feed or media URL can stream an unbounded response to local storage via the temp-file download path, exhausting disk or system resources on the host running the CLI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53781
- https://github.com/steipete/summarize/pull/237
- https://github.com/steipete/summarize/commit/14de194c24c5e0fba4bdb4a6f7766eb6ea3ed750
- https://github.com/steipete/summarize
- https://github.com/steipete/summarize/releases/tag/v0.17.0
- https://www.vulncheck.com/advisories/summarize-disk-exhaustion-via-uncapped-media-download
