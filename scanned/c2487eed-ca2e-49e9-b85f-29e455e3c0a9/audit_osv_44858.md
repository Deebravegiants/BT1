# [H] Open WebUI: Sign-in as another user via wildcard characters in the OAuth subject claim on SQLite

## Summary
Severity: High
Advisory: CVE-2026-87016
Aliases: GHSA-wpmr-8h3q-fwj7
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87016
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.6.41 until 0.11.1, get_user_by_oauth_sub and get_user_by_scim_external_id in backend/open_webui/models/users.py used JSON contains matching that compiled to SQL LIKE substring matching on SQLite. An OAuth subject containing percent or underscore wildcard characters could resolve to a different stored identity, potentially selecting an administrator account and issuing the attacker that account's session; PostgreSQL deployments were not affected. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87016.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-wpmr-8h3q-fwj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-87016
- https://github.com/open-webui/open-webui/commit/73c1f5806aeb6345dad5de8f5aa26d1f3d0bef80
- https://github.com/open-webui/open-webui/pull/28624
