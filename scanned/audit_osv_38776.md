# [C] Plunk: SNS webhook forgery

## Summary
Severity: Critical
Advisory: CVE-2026-42193
Aliases: GHSA-9792-w86v-gx53
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42193
Type: osv

## Details
Plunk is an open-source email platform built on top of AWS SES. Prior to version 0.9.0, the /webhooks/sns endpoint accepts Amazon SNS notification payloads from unauthenticated requests without verifying the SNS signature, certificate, or topic ARN, meaning anyone can forge a valid-looking webhook request. This allows an unauthenticated attacker to spoof SNS events to trigger workflow automations, unsubscribe contacts, manipulate email delivery metrics, and potentially exhaust billing credits. This issue has been patched in version 0.9.0.

## References
- https://github.com/useplunk/plunk/releases/tag/v0.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42193.json
- https://github.com/useplunk/plunk/security/advisories/GHSA-9792-w86v-gx53
- https://nvd.nist.gov/vuln/detail/CVE-2026-42193
