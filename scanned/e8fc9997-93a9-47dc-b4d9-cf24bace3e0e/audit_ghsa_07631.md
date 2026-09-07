# [M] n8n: Webhook Forgery on Github Webhook Trigger

## Summary
Severity: Medium
Advisory: GHSA-mqpr-49jj-32rc
CVE: CVE-2026-56357
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-mqpr-49jj-32rc
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.15
- npm: `n8n` — affected >=2.0.0 <2.5.0

## Details
## Impact
An attacker who knows the webhook URL of a workflow using the GitHub Webhook Trigger node could send unsigned POST requests and trigger the workflow with arbitrary data. The node did not implement the HMAC-SHA256 signature verification that GitHub provides to authenticate webhook deliveries, allowing any party to spoof GitHub webhook events.

## Patches
The issue has been fixed in n8n versions 2.5.0 and 1.123.15. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Restrict network access to the n8n webhook endpoint to known GitHub webhook IP ranges.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mqpr-49jj-32rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-56357
- https://github.com/n8n-io/n8n/commit/a19347a6bc9a96d5065ac77d25a811e46178c578
- https://github.com/n8n-io/n8n/commit/afe322325502f448b33bff1db1575e4447c28a36
- https://github.com/n8n-io/n8n
- https://www.vulncheck.com/advisories/n8n-webhook-forgery-via-missing-hmac-sha256-signature-verification-in-github-webhook-trigger
