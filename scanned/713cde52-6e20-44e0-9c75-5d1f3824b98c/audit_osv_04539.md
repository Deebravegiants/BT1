# [M] Discourse has inferable private group membership or existence via exclude_groups parameter

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33425
Aliases: CVE-2026-33425, GHSA-r6rh-xvf5-r5f2
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33425
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, unauthenticated users can determine whether a specific user is a member of a private group by observing changes in directory results when using the `exclude_groups` parameter. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. As a workaround, disable public access to the user directory via Admin → Settings → hide user profiles from public.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-r6rh-xvf5-r5f2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33425
