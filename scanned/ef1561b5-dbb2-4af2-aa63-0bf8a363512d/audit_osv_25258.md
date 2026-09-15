# [M] Zulip vulnerable to insufficient authorization check for edition/deletion of messages and topics in private streams by former subscribers

## Summary
Severity: Medium
Advisory: CVE-2023-32678
Aliases: GHSA-q3wg-jm9p-35fj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-08-25
Source: https://osv.dev/vulnerability/CVE-2023-32678
Type: osv

## Details
Zulip is an open-source team collaboration tool with topic-based threading that combines email and chat. Users who used to be subscribed to a private stream and have been removed from it since retain the ability to edit messages/topics, move messages to other streams, and delete messages that they used to have access to, if other relevant organization permissions allow these actions. For example, a user may be able to edit or delete their old messages they posted in such a private stream. An administrator will be able to delete old messages (that they had access to) from the private stream. This issue was fixed in Zulip Server version 7.3.

## References
- https://zulip.readthedocs.io/en/latest/overview/changelog.html#zulip-server-7-3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32678.json
- https://github.com/zulip/zulip/security/advisories/GHSA-q3wg-jm9p-35fj
- https://nvd.nist.gov/vuln/detail/CVE-2023-32678
