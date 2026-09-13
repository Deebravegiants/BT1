# [H] CVE-2017-0375

## Summary
Severity: High
Advisory: CVE-2017-0375
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-09
Source: https://osv.dev/vulnerability/CVE-2017-0375
Type: osv

## Details
The hidden-service feature in Tor before 0.3.0.8 allows a denial of service (assertion failure and daemon exit) in the relay_send_end_cell_from_edge_ function via a malformed BEGIN cell.

## References
- http://www.securityfocus.com/bid/99017
- https://lists.torproject.org/pipermail/tor-announce/2017-June/000131.html
- https://trac.torproject.org/projects/tor/ticket/22493
- https://github.com/torproject/tor/commit/79b59a2dfcb68897ee89d98587d09e55f07e68d7
