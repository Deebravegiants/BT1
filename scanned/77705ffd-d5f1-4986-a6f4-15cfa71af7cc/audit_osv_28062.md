# [M] Moving single messages from public to private streams leaves them accessible

## Summary
Severity: Medium
Advisory: CVE-2024-27286
Aliases: GHSA-478x-rfqr-w4jf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-27286
Type: osv

## Details
Zulip is an open-source team collaboration tool. When a user moves a Zulip message, they have the option to move all messages in the topic, move only subsequent messages as well, or move just a single message.  If the user chose to just move one message, and was moving it from a public stream to a private stream, Zulip would successfully move the message, -- but active users who did not have access to the private stream, but whose client had already received the message, would continue to see the message in the public stream until they reloaded their client.  Additionally, Zulip did not remove view permissions on the message from recently-active users, allowing the message to show up in the "All messages" view or in search results, but not in "Inbox" or "Recent conversations" views. While the bug has been present since moving messages between streams was first introduced in version 3.0, this option became much more common starting in Zulip 8.0, when the default option in the picker for moving the very last message in a conversation was changed. This issue is fixed in Zulip Server 8.3. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27286.json
- https://github.com/zulip/zulip/security/advisories/GHSA-478x-rfqr-w4jf
- https://nvd.nist.gov/vuln/detail/CVE-2024-27286
- https://github.com/zulip/zulip/commit/3db1733310ddd944c2e690ba673232345c928eec
