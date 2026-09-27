# [M] n8n's Missing Stripe-Signature Verification Allows Unauthenticated Forged Webhooks

## Summary
Severity: Medium
Advisory: GHSA-jf52-3f2h-h9j5
CVE: CVE-2026-21894
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-jf52-3f2h-h9j5
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0.150.0 <2.2.2

## Details
### Impact
An authentication bypass in the Stripe Trigger node allows unauthenticated parties to trigger workflows by sending forged Stripe webhook events.

The Stripe Trigger creates and stores a Stripe webhook signing secret when registering the webhook endpoint, but incoming webhook requests were not verified against this secret. As a result, any HTTP client that knows the webhook URL could send a POST request containing a matching event `type`, causing the workflow to execute as if a legitimate Stripe event had been received.

This issue affects n8n users who have active workflows using the Stripe Trigger node. An attacker could potentially fake payment or subscription events and influence downstream workflow behavior. The practical risk is reduced by the fact that the webhook URL contains a high-entropy UUID; however, authenticated n8n users with access to the workflow can view this webhook ID.

### Patches
The issue has been fixed in n8n version 2.2.2. Users should upgrade to this version or later to ensure that Stripe webhook signatures are properly verified.

### Workarounds
There is no complete workaround short of upgrading. As a temporary mitigation, users can deactivate affected workflows or restrict access to workflows containing Stripe Trigger nodes to trusted users only.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jf52-3f2h-h9j5
- https://nvd.nist.gov/vuln/detail/CVE-2026-21894
- https://github.com/n8n-io/n8n/pull/22764
- https://github.com/n8n-io/n8n/commit/a61a5991093c41863506888336e808ac1eff8d59
- https://github.com/n8n-io/n8n
