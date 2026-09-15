# [C] CVE-2026-16624

## Summary
Severity: Critical
Advisory: CVE-2026-16624
Aliases: GHSA-4fwh-xxpv-xfm6
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-16624
Type: osv

## Details
Cal.com OSS ships lacks authorization on webhook teamId creation, allowing any authenticated user to create a webhook on any team via unvalidated teamId injection, then steal booking data, including fields like organizer/attendee emails and custom responses, and conditionally video-call passwords, by triggering webhook delivery.

## References
- https://vokecyber.com/research/calcom-cross-tenant-webhook-plant
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16624.json
- https://github.com/calcom/cal.diy/security/advisories/GHSA-4fwh-xxpv-xfm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-16624
