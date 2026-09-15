# [M] CVE-2017-0881

## Summary
Severity: Medium
Advisory: CVE-2017-0881
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-03-28
Source: https://osv.dev/vulnerability/CVE-2017-0881
Type: osv

## Details
An error in the implementation of an autosubscribe feature in the check_stream_exists route of the Zulip group chat application server before 1.4.3 allowed an authenticated user to subscribe to a private stream that should have required an invitation from an existing member to join. The issue affects all previously released versions of the Zulip server.

## References
- http://www.securityfocus.com/bid/97159
- https://github.com/zulip/zulip/commit/7ecda1ac8e26d8fb3725e954b2dc4723dda2255f
- https://groups.google.com/d/msg/zulip-announce/VyawgRuoY34/NTBwnTArGwAJ
