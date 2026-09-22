# [M] CVE-2019-16215

## Summary
Severity: Medium
Advisory: CVE-2019-16215
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-18
Source: https://osv.dev/vulnerability/CVE-2019-16215
Type: osv

## Details
The Markdown parser in Zulip server before 2.0.5 used a regular expression vulnerable to exponential backtracking. A user who is logged into the server could send a crafted message causing the server to spend an effectively arbitrary amount of CPU time and stall the processing of future messages.

## References
- https://blog.zulip.org/2019/09/11/zulip-server-2-0-5-security-release/
- https://github.com/zulip/zulip/commit/5797f013b3be450c146a4141514bda525f2f1b51
