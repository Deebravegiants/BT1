# [H] OpenClaw: Feishu webhook mode accepted forged events when only `verificationToken` was configured

## Summary
Severity: High
Advisory: GHSA-g353-mgv3-8pcj
CVE: CVE-2026-32974
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-g353-mgv3-8pcj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

Feishu webhook mode allowed deployments that configured only `verificationToken` without `encryptKey`. In that state, forged inbound events could be accepted because the weaker configuration did not provide the required cryptographic verification boundary.

### Impact

An unauthenticated network attacker who could reach the webhook endpoint could inject forged Feishu events, impersonate senders, and potentially trigger downstream tool execution subject to the local agent policy.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. Feishu webhook mode now fails closed unless `encryptKey` is configured, and the webhook transport rejects missing or invalid signatures before dispatch. Update to `2026.3.12` or later and configure `encryptKey` for webhook deployments.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g353-mgv3-8pcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32974
- https://github.com/openclaw/openclaw/pull/44087
- https://github.com/openclaw/openclaw/commit/7844bc89a1612800810617c823eb0c76ef945804
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
- https://www.vulncheck.com/advisories/openclaw-forged-event-injection-via-feishu-webhook-verification-token
