# [M] Discourse: Prevent webhook payload disclosure on event redelivery

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-47263
Aliases: CVE-2026-47263, GHSA-wvrm-9v64-m96p
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-47263
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, the MessageBus.publish call for /web_hook_events/<id> in Jobs::RedeliverWebHookEvents did not pass group_ids, leaving the channel readable by any authenticated user (or anonymous user on instances where login_required is disabled). Webhook IDs are sequential integers and trivially enumerable. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-wvrm-9v64-m96p
- https://nvd.nist.gov/vuln/detail/CVE-2026-47263
