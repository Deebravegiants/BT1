# [M] LiveHelperChat has department-level authorization bypass in holdaction, blockuser, and transferchat endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-27954
Aliases: GHSA-87wc-2p86-h3w7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27954
Type: osv

## Details
Live Helper Chat is an open-source application that enables live support websites. In versions up to and including 4.52, three chat action endpoints  (holdaction.php, blockuser.php, and transferchat.php) load chat objects by ID without calling `erLhcoreClassChat::hasAccessToRead()`, allowing operators to act on chats in departments they are not assigned to. Operators with the relevant role permissions (holduse, allowblockusers, allowtransfer) can hold, block users from, or transfer chats in departments they are not assigned to. This is a horizontal privilege escalation within one organization. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27954.json
- https://github.com/LiveHelperChat/livehelperchat/security/advisories/GHSA-87wc-2p86-h3w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27954
