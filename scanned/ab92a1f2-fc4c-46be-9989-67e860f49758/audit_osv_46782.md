# [H] CVE-2015-2688

## Summary
Severity: High
Advisory: CVE-2015-2688
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/CVE-2015-2688
Type: osv

## Details
buf_pullup in Tor before 0.2.4.26 and 0.2.5.x before 0.2.5.11 does not properly handle unexpected arrival times of buffers with invalid layouts, which allows remote attackers to cause a denial of service (assertion failure and daemon exit) via crafted packets.

## References
- https://lists.torproject.org/pipermail/tor-talk/2015-March/037281.html
- https://trac.torproject.org/projects/tor/ticket/15083
- https://lists.torproject.org/pipermail/tor-talk/2015-March/037281.html
- https://trac.torproject.org/projects/tor/ticket/15083
