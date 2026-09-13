# [M] Wallos: iCalendar Injection via CRLF in Subscription Name/Notes Export

## Summary
Severity: Medium
Advisory: CVE-2026-77353
Aliases: GHSA-q2r8-m9wm-5547
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-77353
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 5.0.0, Wallos allows authenticated users to inject arbitrary iCalendar properties and events into their exported .ics feed by embedding raw CRLF sequences in subscription names or notes. Because the input validation layer only encodes HTML metacharacters but never strips newlines, and the export layer decodes those entities back before writing iCal output, an attacker with any valid account can craft a subscription whose name breaks out of the current VEVENT block and inserts fully attacker-controlled calendar events — including spoofed organizers, arbitrary email addresses in ATTENDEE properties, and misleading event content — into any calendar application subscribed to that feed. This issue has been patched in version 5.0.0.

## References
- https://github.com/ellite/Wallos/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77353.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-q2r8-m9wm-5547
- https://nvd.nist.gov/vuln/detail/CVE-2026-77353
- https://github.com/ellite/Wallos/commit/11eaf402e841a628c68a805694227ce66c45f6f3
