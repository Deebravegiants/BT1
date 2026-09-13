# [M] Ory Oathkeeper has an authentication bypass by usage of untrusted header

## Summary
Severity: Medium
Advisory: GHSA-vhr5-ggp3-qq85
CVE: CVE-2026-33495
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-vhr5-ggp3-qq85
Type: github-advisory

## Affected
- Go: `github.com/ory/oathkeeper` — affected >=0 <0.40.10-0.20260320084810-e9acca14a04d

## Details
## Description

Ory Oathkeeper is often deployed behind other components like CDNs, WAFs, or reverse proxies. Depending on the setup, another component might forward the request to the Oathkeeper proxy with a different protocol (http vs. https) than the original request. In order to properly match the request against the configured rules, Oathkeeper considers the `X-Forwarded-Proto`  header when evaluating rules. The configuration option `serve.proxy.trust_forwarded_headers` (defaults to false) governs whether this and other `X-Forwarded-*` headers should be trusted. Oathkeeper did not properly respect this configuration, and would always consider the `X-Forwarded-Proto`  header.

## Preconditions

In order for an attacker to abuse this, an installation of Ory Oathkeeper needs to have distinct rules for HTTP and HTTPS requests. Also, the attacker needs to be able to trigger one but not the other rule. In this scenario, the attacker can send the same request but with the `X-Forwarded-Proto`  header in order to trigger the other rule. We do not expect many configurations to meet these preconditions.

## Mitigation

It is generally recommended to drop any unexpected headers as early as possible when a request is handled, e.g. in the WAF.

Ory Oathkeeper will correctly respect the `serve.proxy.trust_forwarded_headers` configuration going forward, thereby eliminating the attack scenario. We recommend upgrading to a fixed version even if the preconditions are not met.

## References
- https://github.com/ory/oathkeeper/security/advisories/GHSA-vhr5-ggp3-qq85
- https://nvd.nist.gov/vuln/detail/CVE-2026-33495
- https://github.com/ory/oathkeeper/commit/e9acca14a04d246250557550065e4b4576525bd5
- https://github.com/ory/oathkeeper
