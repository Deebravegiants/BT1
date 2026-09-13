# [M] Solidtime team page exposes pending invitation and member emails to employees who lack invitations:view/members:view permission

## Summary
Severity: Medium
Advisory: CVE-2026-47236
Aliases: GHSA-33xq-wf67-c7vh
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47236
Type: osv

## Details
Solidtime is an open-source time-tracking app. Prior to version 0.12.2, Solidtime defines an explicit invitations:view and members:view permissions that gates the official invitations and members API. The Jetstream web team page authorizes access with only belongsToTeam() and then loads and serializes all pending invitation emails as well as members into Inertia props. Any employee who belongs to the organization can read pending invitation email addresses and members through the serialised inertia data in the team page body even though the same user is forbidden from the API. This issue has been patched in version 0.12.2.

## References
- https://github.com/solidtime-io/solidtime/releases/tag/v0.12.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47236.json
- https://github.com/solidtime-io/solidtime/security/advisories/GHSA-33xq-wf67-c7vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-47236
