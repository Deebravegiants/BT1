# [H] Suna < 0.9.102 Broken Access Control via Message Queue API

## Summary
Severity: High
Advisory: CVE-2026-66027
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66027
Type: osv

## Details
Suna before 0.9.102 contains a broken access control vulnerability in the message queue API that allows authenticated attackers to access and manipulate queue resources belonging to other users by exploiting missing ownership and account isolation checks. Attackers can read pending prompt queues of all users, read or delete individual sessions, and inject arbitrary prompts into another user's session queue, causing the background drainer to forward malicious messages to the victim's running AI agent with the victim's credentials and permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66027.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66027
- https://www.vulncheck.com/advisories/suna-broken-access-control-via-message-queue-api
- https://github.com/kortix-ai/suna/commit/7536a7d47fc93abcb66e677fcc993b390c81296a
- https://github.com/kortix-ai/suna/pull/4373
- https://github.com/kortix-ai/suna/releases/tag/v0.9.102
- https://github.com/kortix-ai/suna
- https://github.com/geo-chen/oss/blob/main/suna.md
