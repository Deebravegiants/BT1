# [M] Summarize's hover summary feature allows malicious pages to dispatch synthetic mouseover events over attacker-controlled links

## Summary
Severity: Medium
Advisory: GHSA-2r69-qgv3-hr65
CVE: CVE-2026-45245
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-2r69-qgv3-hr65
Type: github-advisory

## Affected
- npm: `@steipete/summarize` — affected >=0 <0.15.1

## Details
Summarize prior to 0.15.0 contains a vulnerability in the hover summary feature that allows malicious pages to dispatch synthetic mouseover events over attacker-controlled links, causing the extension to make authenticated daemon requests using stored tokens without verifying event trustworthiness. Attackers can place local or private-network URLs behind hoverable links to route authenticated requests through the daemon, potentially accessing sensitive internal endpoints when users interact with attacker-controlled content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45245
- https://github.com/steipete/summarize/pull/218
- https://github.com/steipete/summarize/commit/ecbb2c414255aa480a15d0d8b205224c14cfdbcb
- https://github.com/steipete/summarize
- https://github.com/steipete/summarize/releases/tag/v0.15.1
- https://github.com/steipete/summarize/releases/tag/v0.15.2
- https://www.vulncheck.com/advisories/summarize-unauthorized-daemon-request-via-untrusted-events
