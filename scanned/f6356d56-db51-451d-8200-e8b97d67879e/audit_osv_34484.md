# [M] Improper Authorization in danny-avila/librechat

## Summary
Severity: Medium
Advisory: CVE-2025-6088
CVSS: 4.2 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-6088
Type: osv

## Details
In version 0.7.8 of danny-avila/librechat, improper authorization controls in the conversation sharing feature allow unauthorized access to other users' conversations if the conversation ID is known. Although UUIDv4 conversation IDs are generated server-side and are difficult to brute force, they can be obtained from less-protected sources such as server-side access logs, browser history, or screenshots. The vulnerability permits a logged-in user to gain read-only access to another user's conversations by exploiting the `/api/share/conversationID` endpoint, which lacks authorization checks. This issue is resolved in version v0.7.9-rc1.

## References
- https://huntr.com/bounties/361405bb-a739-41eb-a680-4cb6193e7c76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6088.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6088
- https://github.com/danny-avila/librechat/commit/3af2666890bbf291cb7b9f3e03592d54714f0ff5
