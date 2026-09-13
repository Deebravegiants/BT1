# [M] CVE-2021-30478

## Summary
Severity: Medium
Advisory: CVE-2021-30478
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-04-15
Source: https://osv.dev/vulnerability/CVE-2021-30478
Type: osv

## Details
An issue was discovered in Zulip Server before 3.4. A bug in the implementation of the can_forge_sender permission (previously is_api_super_user) resulted in users with this permission being able to send messages appearing as if sent by a system bot, including to other organizations hosted by the same Zulip installation.

## References
- https://blog.zulip.com/2021/04/14/zulip-server-3-4/
