# [M] CVE-2021-30477

## Summary
Severity: Medium
Advisory: CVE-2021-30477
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-04-15
Source: https://osv.dev/vulnerability/CVE-2021-30477
Type: osv

## Details
An issue was discovered in Zulip Server before 3.4. A bug in the implementation of replies to messages sent by outgoing webhooks to private streams meant that an outgoing webhook bot could be used to send messages to private streams that the user was not intended to be able to send messages to.

## References
- https://blog.zulip.com/2021/04/14/zulip-server-3-4/
