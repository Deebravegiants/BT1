# [C] Penpot: Pre-authenticated account takeover via team-invitation token + prepare-register-profile

## Summary
Severity: Critical
Advisory: CVE-2026-44986
Aliases: GHSA-4937-35vc-hqjj
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-44986
Type: osv

## Details
Penpot is an open-source design tool for design and code collaboration. Prior to 2.14.5, Penpot exposed teams_invitations.clj invitation tokens from create-team-invitations, embedded an existing profile id in auth.clj prepare-register-profile, and had auth.clj register-profile issue a session based on the invitation email match without password verification, allowing a registered user to take over any non-blocked profile. This issue is fixed in version 2.14.5.

## References
- https://github.com/penpot/penpot/releases/tag/2.14.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44986.json
- https://github.com/penpot/penpot/security/advisories/GHSA-4937-35vc-hqjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44986
- https://github.com/penpot/penpot/commit/9e681260ccc4feb6c564ff0773fb9594b462c574
- https://github.com/penpot/penpot/pull/9380
