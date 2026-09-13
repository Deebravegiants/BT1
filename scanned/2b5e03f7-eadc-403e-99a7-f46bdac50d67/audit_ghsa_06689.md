# [M] n8n: Google Service Account Private Key Exposed in JWT Header

## Summary
Severity: Medium
Advisory: GHSA-9r8p-h6cc-6qhm
CVE: CVE-2026-65599
CWE: CWE-312
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:N/VA:N/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-9r8p-h6cc-6qhm
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact
When n8n was configured with a Google Service Account key, the full PEM private key was mistakenly placed in the JWT header's `kid` field (which should only have held a key identifier). Since JWT headers were Base64-encoded rather than encrypted, the key could be recovered by anything that logged or inspected the JWT.

An attacker who obtained the key could impersonate the service account and access or modify any Google Cloud resource it was authorized to use.

Only instances using Google Service Account credentials are affected.

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Avoid using Google Service Account credentials until the instance is patched.
- Rotate any Google Service Account keys that may have been used with an affected n8n version.
- Review proxy, load balancer, and application logs for JWT headers that may contain exposed key material and treat any such keys as compromised.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9r8p-h6cc-6qhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-65599
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-credential-exposure-via-jwt-header
