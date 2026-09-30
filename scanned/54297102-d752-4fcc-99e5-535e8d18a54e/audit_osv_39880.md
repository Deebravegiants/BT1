# [M] OpenReception's schedule endpoint discloses isPublic=false channels and slot availability to unauthenticated callers

## Summary
Severity: Medium
Advisory: CVE-2026-48078
Aliases: GHSA-v6fw-m2mg-5gr9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48078
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Prior to version 1.0.5, the unauthenticated `/api/tenants/{id}/schedule` endpoint returns every non-archived channel for a tenant regardless of the channel's `isPublic` flag. Channels marked `isPublic = false` are intended to be invisible to public callers; the dashboard creates them deliberately to hide internal-only services from the patient booking UI. The schedule endpoint ignores the flag entirely and discloses channel names, descriptions, IDs, agent associations, pause status, confirmation requirements, and computed slot availability for the requested date range. The asymmetry between `addAppointmentToTunnel` (which enforces `eq(channel.isPublic, true)`) and the schedule endpoint (which does not) confirms the design intent: private channels exist as a real access boundary in the booking flow, just not in the schedule disclosure. Version 1.0.5 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48078.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-v6fw-m2mg-5gr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48078
- https://github.com/open-reception/appointment-booking-software/commit/f47320dd8a236750442a60cb32829b04e99eb8df
