# [M] Cocotais Bot has builtin .echo command injection

## Summary
Severity: Medium
Advisory: GHSA-mj2c-8hxf-ffvq
CVE: CVE-2025-47948
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-mj2c-8hxf-ffvq
Type: github-advisory

## Affected
- npm: `cocotais-bot` — affected >=1.5.0-test2-hotfix <1.6.2

## Details
### Summary
﻿
A command echoing feature in the framework allows users to indirectly trigger privileged behavior by injecting special platform tags. Specifically, an unauthorized user can use the `/echo <qqbot-at-everyone />` command to cause the bot to send a message that mentions all members in the chat, bypassing any permission controls. This can lead to spam, disruption, or abuse of notification systems.
﻿
### Details
﻿
The framework provides a command `/echo` that causes the bot to repeat any user-provided message verbatim in the group chat. However, the bot fails to sanitize or filter platform-specific control elements such as `<qqbot-at-everyone />`, which, when included in a message, mentions everyone (i.e., @全体成员). While normal users are forbidden from using this tag in normal chats, the bot, which has higher privileges, is allowed to do so.
﻿
Since the `/echo` command blindly echoes any content, a user can exploit this by sending:
﻿
```
/echo <qqbot-at-everyone />
```
﻿
The bot will then send a message containing `<qqbot-at-everyone />`, causing the platform to interpret it as an @全体成员 command, effectively allowing an unauthorized user to @everyone via the bot.
﻿
### PoC
﻿
1. Set up a chatbot using the affected framework.
2. Join the chat that includes the bot as a regular user with **no permission to use @全体成员**.
3. Send the following message in the chat:
﻿
```
/echo <qqbot-at-everyone />
```
4. The bot will respond by repeating the message, and the platform will interpret `<qqbot-at-everyone />` as an @全体成员 mention.
5. All the chat members receive a notification, despite the user lacking that permission.
﻿
﻿

## References
- https://github.com/cocotais/cocotais-bot/security/advisories/GHSA-mj2c-8hxf-ffvq
- https://nvd.nist.gov/vuln/detail/CVE-2025-47948
- https://github.com/cocotais/cocotais-bot/commit/d1cf01a9a41b3131241d1833444b890c8d6e70b8
- https://github.com/cocotais/cocotais-bot
