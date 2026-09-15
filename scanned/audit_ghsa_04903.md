# [M] Bugsink: DOS using large numbers of event tags

## Summary
Severity: Medium
Advisory: GHSA-5x67-j5xg-c5gj
CVE: CVE-2026-53954
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-5x67-j5xg-c5gj
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=0 <2.2.2

## Details
### Summary

In affected versions, Bugsink stores every tag supplied with an incoming event. An event with an unusually large number
of custom (i.e. supplied by an attacker) tags can therefore make ingestion spend more time than intended writing tag rows.

Bugsink uses a single-writer database architecture. That keeps the implementation simple, but it also means one
expensive write transaction can delay other event digestion while it is running. In this case, it makes ingestion of
other events wait until the transaction that writes the tags finishes, which effectively causes a temporary denial of
service for other events.

### Impact

Submitting such an event requires a valid project DSN. DSNs are sometimes visible in client-side applications, so they
should not be treated as a strong security boundary, but the issue is still limited to ingestion for a Bugsink instance
that accepts the event.

The impact is availability-only. The issue does not expose stored data, modify existing events, or allow code execution.

### Mitigation

Update to version 2.2.2, which caps the number of tags stored for a single event. The default cap is 100 tags and can
be changed with `MAX_EVENT_TAGS`.

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-5x67-j5xg-c5gj
- https://github.com/bugsink/bugsink
- https://github.com/bugsink/bugsink/releases/tag/2.2.2
