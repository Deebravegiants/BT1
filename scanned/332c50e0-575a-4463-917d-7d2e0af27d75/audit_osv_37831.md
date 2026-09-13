# [M] Frigate has cross-camera snapshot disclosure via unrestricted timeline IDs and missing authorization in /api/events/{event_id}/snapshot-clean.webp

## Summary
Severity: Medium
Advisory: CVE-2026-33470
Aliases: GHSA-m2mg-pj9p-2r7g
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33470
Type: osv

## Details
Frigate is a network video recorder (NVR) with realtime local object detection for IP cameras. In version 0.17.0, a low-privilege authenticated user restricted to one camera can access snapshots from other cameras. This is possible through a chain of two authorization problems: `/api/timeline` returns timeline entries for cameras outside the caller's allowed camera set, then `/api/events/{event_id}/snapshot-clean.webp` declares `Depends(require_camera_access)` but never actually validates `event.camera` after looking up the event. Together, this allows a restricted user to enumerate event IDs from unauthorized cameras and then fetch clean snapshots for those events. Version 0.17.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33470.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-m2mg-pj9p-2r7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33470
