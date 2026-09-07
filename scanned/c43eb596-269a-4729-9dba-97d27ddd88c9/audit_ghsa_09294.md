# [H] LiteLLM allows a user to modify their own user_role via the /user/update endpoint

## Summary
Severity: High
Advisory: GHSA-wpfp-gwwc-vwq6
CVE: CVE-2026-47102
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-wpfp-gwwc-vwq6
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.83.10

## Details
LiteLLM prior to 1.83.10 allows a user to modify their own user_role via the /user/update endpoint. While the endpoint correctly restricts users to updating only their own account, it does not restrict which fields may be changed. A user who can reach this endpoint can set their role to proxy_admin, gaining full administrative access to LiteLLM including all users, teams, keys, models, and prompt history. Users with the org_admin role have legitimate access to this endpoint and can exploit this vulnerability without chaining any additional flaw.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47102
- https://github.com/BerriAI/litellm/pull/25541
- https://github.com/BerriAI/litellm/commit/128d32d2494b759c5d15da3452452af4c6a34c01
- https://github.com/BerriAI/litellm/commit/e6f18ce75b111c9b93dc15c72894cbdeb53177ce
- https://gist.github.com/13ph03nix/9ec616e1fdc77b3673509c60206e827f
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.83.10-stable
- https://huntr.com/bounties/8e75edfb-ff05-4e63-bfca-2d93d03fb3b9
- https://www.obsidiansecurity.com/blog/litellm-privilege-escalation-rce
- https://www.vulncheck.com/advisories/litellm-privilege-escalation-via-user-update
