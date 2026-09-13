# [H] Chamilo: Friend Request Workflow Bypass - Unauthorized Friend Addition and ID Validation Bypass

## Summary
Severity: High
Advisory: CVE-2025-52469
Aliases: GHSA-m5xj-5xf3-rqch
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-52469
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, a logic vulnerability in the friend request workflow of Chamilo’s social network module allows an authenticated user to forcibly add any user as a friend by directly calling the AJAX endpoint. The attacker can bypass the normal flow of sending and accepting friend requests, and even add non-existent users. This breaks access control and social interaction logic, with potential privacy implications. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52469.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-m5xj-5xf3-rqch
- https://nvd.nist.gov/vuln/detail/CVE-2025-52469
- https://github.com/chamilo/chamilo-lms/commit/39e0fa88a2ba5dd197e0d8ce7335730b666992a6
