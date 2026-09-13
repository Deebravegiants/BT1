# [H] CVE-2017-0376

## Summary
Severity: High
Advisory: CVE-2017-0376
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-09
Source: https://osv.dev/vulnerability/CVE-2017-0376
Type: osv

## Details
The hidden-service feature in Tor before 0.3.0.8 allows a denial of service (assertion failure and daemon exit) in the connection_edge_process_relay_cell function via a BEGIN_DIR cell on a rendezvous circuit.

## References
- http://www.debian.org/security/2017/dsa-3877
- https://lists.torproject.org/pipermail/tor-announce/2017-June/000131.html
- https://trac.torproject.org/projects/tor/ticket/22494
- https://github.com/torproject/tor/commit/56a7c5bc15e0447203a491c1ee37de9939ad1dcd
