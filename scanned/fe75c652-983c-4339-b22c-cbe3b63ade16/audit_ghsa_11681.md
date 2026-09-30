# [M] Egress Policy Bypass via DNS over TCP in Harden-Runner (Community Tier)

## Summary
Severity: Medium
Advisory: GHSA-g699-3x6g-wm3g
CVE: CVE-2026-32946
CWE: CWE-693, CWE-863
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-g699-3x6g-wm3g
Type: github-advisory

## Affected
- GitHub Actions: `step-security/harden-runner` — affected >=0 <2.16.0

## Details
## Summary

A vulnerability exists in the Community Tier of Harden-Runner that allows bypassing the `egress-policy: block` network restriction using DNS queries over TCP.

Harden-Runner enforces egress policies on GitHub runners by filtering outbound connections at the network layer. When `egress-policy: block` is enabled with a restrictive allowed-endpoints list (e.g., only `github.com:443`), all non-compliant traffic should be denied. However, DNS queries over TCP, commonly used for large responses or fallback from UDP, are not adequately restricted. Tools like `dig` can explicitly initiate TCP-based DNS queries (`+tcp` flag) without being blocked. 

This vulnerability requires the attacker to already have code execution capabilities within the GitHub Actions workflow.

The Enterprise Tier of Harden-Runner is **not affected** by this vulnerability.

## Impact

When Harden-Runner is configured with `egress-policy: block` and a restrictive `allowed-endpoints` list, an attacker with existing code execution capabilities within a GitHub Actions workflow can bypass the egress block policy by initiating DNS queries over TCP to external resolvers. This allows outbound network communication that evades the configured network restrictions.

This vulnerability affects only the Community Tier. It requires the attacker to already have code execution capabilities within the GitHub Actions workflow.

## Remediation

### For Community Tier Users

Upgrade to Harden-Runner v2.16.0 or later. 

### For Enterprise Tier Users

No action required. Enterprise tier customers are not affected by this vulnerability.

## Credit 

We would like to thank [Devansh Batham](https://github.com/devanshbatham) for responsibly disclosing this vulnerability through our security reporting process.

## References
- https://github.com/step-security/harden-runner/security/advisories/GHSA-g699-3x6g-wm3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-32946
- https://github.com/step-security/harden-runner
- https://github.com/step-security/harden-runner/releases/tag/v2.16.0
