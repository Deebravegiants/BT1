# [M] Authenticated PostHog users vulnerable to SSRF

## Summary
Severity: Medium
Advisory: CVE-2023-46746
Aliases: GHSA-wqqw-r8c5-j67c
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-12-01
Source: https://osv.dev/vulnerability/CVE-2023-46746
Type: osv

## Details
PostHog provides open-source product analytics, session recording, feature flagging and A/B testing that you can self-host. A server-side request forgery (SSRF), which can only be exploited by authenticated users, was found in Posthog. Posthog did not verify whether a URL was local when enabling webhooks, allowing authenticated users to forge a POST request. This vulnerability has been addressed in `22bd5942` and will be included in subsequent releases. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46746.json
- https://github.com/PostHog/posthog/security/advisories/GHSA-wqqw-r8c5-j67c
- https://nvd.nist.gov/vuln/detail/CVE-2023-46746
- https://securitylab.github.com/advisories/GHSL-2023-185_posthog_posthog/
- https://github.com/PostHog/posthog/commit/22bd5942638d5d9bc4bd603a9bfe8f8a95572292
