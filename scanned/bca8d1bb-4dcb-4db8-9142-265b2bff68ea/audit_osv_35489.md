# [H] Insecure Direct Object Reference (IDOR) in parisneo/lollms

## Summary
Severity: High
Advisory: CVE-2026-0562
Aliases: PYSEC-2026-204
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-03-29
Source: https://osv.dev/vulnerability/CVE-2026-0562
Type: osv

## Details
A critical security vulnerability in parisneo/lollms versions up to 2.2.0 allows any authenticated user to accept or reject friend requests belonging to other users. The `respond_request()` function in `backend/routers/friends.py` does not implement proper authorization checks, enabling Insecure Direct Object Reference (IDOR) attacks. Specifically, the `/api/friends/requests/{friendship_id}` endpoint fails to verify whether the authenticated user is part of the friendship or the intended recipient of the request. This vulnerability can lead to unauthorized access, privacy violations, and potential social engineering attacks. The issue has been addressed in version 2.2.0.

## References
- https://aydinnyunus.github.io/2026/04/18/idor-lollms-friend-request-cve-2026-0562/
- https://huntr.com/bounties/6aab01ca-a138-4a1d-bef9-3bce145359bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0562.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0562
- https://github.com/parisneo/lollms/commit/c46297799f8e1e23305373f8350746b905e0e83c
