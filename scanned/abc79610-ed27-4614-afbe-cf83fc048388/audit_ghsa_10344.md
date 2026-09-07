# [M] Valtimo: Sensitive data exposure through inbox message logging in InboxHandlingService

## Summary
Severity: Medium
Advisory: GHSA-hfrg-mcvw-8mch
CVE: CVE-2026-34164
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-hfrg-mcvw-8mch
Type: github-advisory

## Affected
- Maven: `com.ritense.valtimo:inbox` — affected >=13.0.0.RELEASE <13.22.0.RELEASE

## Details
### Summary

The `InboxHandlingService` logs the full content of every incoming inbox message at INFO level (`logger.info("Received message: {}", message)`). Inbox messages are wrappers around outbox message data, which can contain highly sensitive information such as personal data (PII), citizen identifiers (BSN), and case details.

### Impact

This data is exposed to:
- Anyone with access to application logs (stdout/log files)
- Any Valtimo user with the admin role, through the logging module in the Admin UI

### Affected Code

`com.ritense.inbox.InboxHandlingService#handle` in the `inbox` module.

### Resolution

Fixed in [13.22.0](https://github.com/valtimo-platform/valtimo/releases/tag/13.22.0) via commit [`f16a1940ba`](https://github.com/valtimo-platform/valtimo/commit/f16a1940ba7b34627c0b966f98ca78655ace9335) (PR [#497](https://github.com/valtimo-platform/valtimo/pull/497), tracking issue [gzac-issues#653](https://github.com/generiekzaakafhandelcomponent/gzac-issues/issues/653)). The log statement was downgraded from INFO to DEBUG and the message payload was removed from the log output.

### Mitigation

For versions before 13.22.0, consider:
- Restricting access to application logs
- Adjusting the log level for `com.ritense.inbox` to WARN or higher in your application configuration

## References
- https://github.com/valtimo-platform/valtimo/security/advisories/GHSA-hfrg-mcvw-8mch
- https://nvd.nist.gov/vuln/detail/CVE-2026-34164
- https://github.com/generiekzaakafhandelcomponent/gzac-issues/issues/653
- https://github.com/valtimo-platform/valtimo/pull/497
- https://github.com/valtimo-platform/valtimo/commit/f16a1940ba7b34627c0b966f98ca78655ace9335
- https://github.com/valtimo-platform/valtimo
- https://github.com/valtimo-platform/valtimo/releases/tag/13.22.0
