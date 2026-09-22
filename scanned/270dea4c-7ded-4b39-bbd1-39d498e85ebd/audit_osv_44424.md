# [M] R2R Missing Ownership Check Allows Modifying Other Users' Conversations

## Summary
Severity: Medium
Advisory: CVE-2026-82271
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82271
Type: osv

## Details
R2R through 3.6.5 fails to properly validate user ownership in conversation update and message handlers, allowing authenticated users to modify other users' conversations. Attackers can supply arbitrary conversation identifiers to rename conversations and append messages to other users' conversation histories, corrupting state and injecting malicious content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82271.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82271
- https://www.vulncheck.com/advisories/r2r-missing-ownership-check-allows-modifying-other-users-conversations
- https://github.com/SciPhi-AI/R2R/issues/2292
- https://github.com/SciPhi-AI/R2R
- https://github.com/SciPhi-AI/R2R/blob/9c5a94d151f90876bd7eb860f300a8fd662dc481/py/core/main/api/v3/conversations_router.py
