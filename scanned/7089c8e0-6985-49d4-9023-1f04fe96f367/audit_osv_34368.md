# [M] Stalwart vulnerable to Memory Exhaustion via CalDAV Event Expansion

## Summary
Severity: Medium
Advisory: CVE-2025-59045
Aliases: GHSA-xv4r-q6gr-6pfg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-09-10
Source: https://osv.dev/vulnerability/CVE-2025-59045
Type: osv

## Details
Stalwart is a mail and collaboration server. Starting in version 0.12.0 and prior to version 0.13.3, a memory exhaustion vulnerability exists in Stalwart's CalDAV implementation that allows authenticated attackers to cause denial-of-service by triggering unbounded memory consumption through recurring event expansion. An authenticated attacker can crash the Stalwart server by creating recurring events with large payloads and triggering their expansion through CalDAV REPORT requests. A single malicious request expanding 300 events with 1000-character descriptions can consume up to 2 GB of memory. The vulnerability exists in the `ArchivedCalendarEventData.expand` function, which processes CalDAV `REPORT` requests with event expansion. When a client requests recurring events in their expanded form using the `<C:expand>` element, the server stores all expanded event instances in memory without enforcing size limits. Users should upgrade to Stalwart version 0.13.3 or later to receive a fix. If immediate upgrading is not possible, implement memory limits at the container/system level; monitor server memory usage for unusual spikes; consider rate limiting CalDAV REPORT requests; and restrict CalDAV access to trusted users only.

## References
- https://github.com/stalwartlabs/stalwart/blob/main/CHANGELOG.md
- https://github.com/stalwartlabs/stalwart/releases/tag/v0.13.3
- https://tools.ietf.org/html/rfc4791
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59045.json
- https://github.com/stalwartlabs/stalwart/security/advisories/GHSA-xv4r-q6gr-6pfg
- https://nvd.nist.gov/vuln/detail/CVE-2025-59045
- https://github.com/stalwartlabs/stalwart/commit/15762fba2ba335e560b8d25f71af085a8b6b6cf2
