# [M] litellm vulnerable to improper access control in team management

## Summary
Severity: Medium
Advisory: GHSA-qqcv-vg9f-5rr3
CVE: CVE-2024-5710
CWE: CWE-284, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-qqcv-vg9f-5rr3
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.40.15

## Details
berriai/litellm version 1.34.34 is vulnerable to improper access control in its team management functionality. This vulnerability allows attackers to perform unauthorized actions such as creating, updating, viewing, deleting, blocking, and unblocking any teams, as well as adding or deleting any member to or from any teams. The vulnerability stems from insufficient access control checks in various team management endpoints, enabling attackers to exploit these functionalities without proper authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5710
- https://github.com/BerriAI/litellm/commit/da3ae00bd68f451ed8ddf0bc0a9fd34bde5554d6
- https://github.com/BerriAI/litellm/blob/224148d6133ee50801cb129cbd21ccc213992e25/litellm/proxy/auth/user_api_key_auth.py#L1020
- https://github.com/berriai/litellm
- https://huntr.com/bounties/70897f59-a966-4d93-b71e-745e3da91970
