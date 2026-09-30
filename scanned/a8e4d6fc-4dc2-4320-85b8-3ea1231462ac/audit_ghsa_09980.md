# [H] RustFS: Missing admin authorization on notification target endpoints allows unauthenticated configuration of event webhooks

## Summary
Severity: High
Advisory: GHSA-pfcq-4gjr-6gjm
CVE: CVE-2026-40937
CWE: CWE-862
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-pfcq-4gjr-6gjm
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=0

## Details
# Missing Admin Auth on Notification Target Endpoints in RustFS


### Finding Summary

All four notification target admin API endpoints in `rustfs/src/admin/handlers/event.rs` use a `check_permissions` helper that validates authentication only (access key + session token), without performing any admin-action authorization via `validate_admin_request`. Every other admin handler in the codebase correctly calls `validate_admin_request` with a specific `AdminAction`. This is the only admin handler file that skips authorization.

A non-admin user can overwrite a shared admin-defined notification target by name, causing subsequent bucket events to be delivered to an attacker-controlled endpoint. This enables cross-user event interception and audit evasion.

### What Was Proven Live

1. **Authorization bypass on all four endpoints** (03_readonly_user_bypass.py)
   - PUT, GET list, GET arns, DELETE all return 200 for readonly-user
   - Control routes (list-users, kms/status) correctly return 403
   - Unauthenticated requests correctly rejected (403 Signature required)

2. **SSRF via health probe** (04_ssrf_listener_landing.py)
   - HEAD request from rustfs container to attacker-controlled listener
   - No host validation: only scheme check (http/https)

3. **Target hijacking and event exfiltration** (05_target_hijacking.py, 06_full_event_exfil.py)
   - Readonly-user overwrites admin-configured target URL by name
   - Subsequent S3 events delivered to attacker-controlled endpoint
   - Captured event body includes object keys, bucket names, user identities, and request metadata

4. **Audit evasion** (05_target_hijacking.py)
   - Readonly-user can delete unbound targets
   - Readonly-user can overwrite bound targets (silently redirecting events)

### Escalation Vectors Tested But Not Viable

1. **Self-referencing webhook to admin API** (13_self_referencing_test.py)
   - Webhook sends unsigned POST with event JSON body
   - Admin endpoints require SigV4 auth -- unsigned request rejected
   - "Confused deputy" via self-referencing does NOT work

2. **Protocol smuggling via non-HTTP targets**
   - Only 2 target types implemented: webhook and MQTT (`event.rs:613` enforces this)
   - No Redis, Kafka, AMQP, or other protocol targets exist
   - CRLF injection in webhook config fields sanitized by reqwest
   - MQTT uses rumqttc (pure Rust binary protocol client), no raw TCP injection

3. **MQTT target for RCE**
   - No unsafe code in MQTT handler
   - rumqttc 0.29.0 has no known public CVEs
   - No Command::new, template engines, or deserialization of broker responses

4. **Unauth access**
   - Endpoints correctly reject unauthenticated requests (403)
   - Endpoints correctly reject invalid credentials (403)

### Prior Art

No existing advisory covers notification target endpoints. 11 published GHSAs on rustfs/rustfs cover different handlers. Closest:
- CVE-2026-22042 (ImportIam wrong action constant) -- same bug class, different file
- CVE-2026-22043 (deny_only short-circuit) -- different bug class

### Recommendation

Submit via GitHub PVR. The finding is well-supported with live PoC, code references, and clear root cause. The fix is straightforward (add `validate_admin_request` calls to event.rs handlers). Core submission should reference 2-3 focused PoC scripts (readonly bypass, target hijack, event exfil), not the full set of 13 exploratory scripts.


Koda Reef

### Patch
This issue has been patched in version https://github.com/rustfs/rustfs/releases/tag/1.0.0-alpha.94.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-pfcq-4gjr-6gjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40937
- https://github.com/rustfs/rustfs
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-alpha.94
