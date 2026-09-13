# [M] Allstar Reviewbot has Authentication Bypass via Hard-coded Webhook Secret

## Summary
Severity: Medium
Advisory: GHSA-33f4-mjch-7fpr
CVE: CVE-2025-61926
CWE: CWE-798
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-33f4-mjch-7fpr
Type: github-advisory

## Affected
- Go: `github.com/ossf/allstar` — affected >=0 <0.0.0-20250721181116-e004ecb540d6

## Details
A vulnerability in Allstar’s Reviewbot component caused inbound webhook requests to be validated against a hard-coded, shared secret:

https://github.com/ossf/allstar/blob/294ae985cc2facd0918e8d820e4196021aa0b914/pkg/reviewbot/reviewbot.go#L59

The value used for the secret token was compiled into the Allstar binary and could not be configured at runtime. In practice, this meant that every deployment using Reviewbot would validate requests with the same secret unless the operator modified source code and rebuilt the component - an expectation that is not documented and is easy to miss. While Reviewbot is not commonly enabled in standard Allstar setups, we are issuing this advisory to reach any environments where it may have been deployed.

## Affected Versions

All Allstar releases prior to v4.5 that include the Reviewbot code path are affected. Deployments on v4.5 and later are not affected. If you have not enabled or exposed the Reviewbot endpoint, this issue does not apply to your installation.

## Impact

If the Reviewbot endpoint is deployed and reachable, an attacker can bypass authentication by crafting webhook requests that use the known, hard-coded secret. Because signature verification will succeed, Reviewbot would treat these requests as authentic when they should be rejected. Depending on the permissions and automations attached to your deployment, this could allow unauthorized triggering of review actions such as posting automated comments or reviews, influencing checks, or otherwise manipulating repository signals. The primary risk is to the integrity of repository workflows rather than confidentiality or availability, although secondary effects (e.g., noisy automation, misleading reviews, or workflow disruptions) are possible.

## Exploitability

Exploiting this is straightforward and does not require an attacker to be authenticated. Anyone who can send requests to the Reviewbot webhook can reach the vulnerable code.

## References
- https://github.com/ossf/allstar/security/advisories/GHSA-33f4-mjch-7fpr
- https://nvd.nist.gov/vuln/detail/CVE-2025-61926
- https://github.com/ossf/allstar/pull/713
- https://github.com/ossf/allstar/commit/e004ecb540d63ca6f5b1689b41af6c0040a82c73
- https://github.com/ossf/allstar
- https://github.com/ossf/allstar/blob/294ae985cc2facd0918e8d820e4196021aa0b914/pkg/reviewbot/reviewbot.go#L59
- https://pkg.go.dev/vuln/GO-2025-4018
