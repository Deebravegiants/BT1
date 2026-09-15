# [M] CVE-2013-4088

## Summary
Severity: Medium
Advisory: CVE-2013-4088
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-21
Source: https://osv.dev/vulnerability/CVE-2013-4088
Type: osv

## Details
Kernel/Modules/AgentTicketWatcher.pm in Open Ticket Request System (OTRS) 3.0.x before 3.0.21, 3.1.x before 3.1.17, and 3.2.x before 3.2.8 does not properly restrict tickets, which allows remote attackers with a valid agent login to read restricted tickets via a crafted URL involving the ticket split mechanism.

## References
- http://advisories.mageia.org/MGASA-2013-0196.html
- https://bugs.gentoo.org/show_bug.cgi?id=CVE-2013-4088
- https://www.securityfocus.com/bid/60688/discuss
- https://bugs.gentoo.org/show_bug.cgi?id=CVE-2013-4088
- http://archives.neohapsis.com/archives/bugtraq/2013-07/0015.html
