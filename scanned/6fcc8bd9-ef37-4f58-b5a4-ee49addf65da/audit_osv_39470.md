# [M] Apache NimBLE: OOB Read via sizeof(pointer) in Legacy Advertising Report Handler

## Summary
Severity: Medium
Advisory: CVE-2026-45812
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-45812
Type: osv

## Details
Incorrect Calculation of Buffer Size vulnerability in Apache NimBLE when processing Legacy Advertising Report HCI event.

When a single HCI advertising report event bundles multiple reports, NimBLE miscalculated the offset to the next report. This can cause the host to read past the end of the buffer and deliver a GAP event with bogus data to the application.

Severity is low: NimBLE's own controller never batches multiple reports into one event, so this only matters when NimBLE's host is paired with a third-party controller that does.

This issue affects Apache NimBLE: through 1.9.0.

Users are recommended to upgrade to version 1.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45812.json
- https://lists.apache.org/thread/rll5m1ly2vg8jr76lp5ohrtspr5vlofy
- https://nvd.nist.gov/vuln/detail/CVE-2026-45812
- https://github.com/apache/mynewt-nimble/commit/605c7585408bc3674818eeb7b6f478a8aefe9746
