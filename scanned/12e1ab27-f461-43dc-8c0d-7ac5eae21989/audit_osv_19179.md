# [M] CVE-2020-8516

## Summary
Severity: Medium
Advisory: CVE-2020-8516
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-02-02
Source: https://osv.dev/vulnerability/CVE-2020-8516
Type: osv

## Details
The daemon in Tor through 0.4.1.8 and 0.4.2.x through 0.4.2.6 does not verify that a rendezvous node is known before attempting to connect to it, which might make it easier for remote attackers to discover circuit information. NOTE: The network team of Tor claims this is an intended behavior and not a vulnerability

## References
- https://lists.torproject.org/pipermail/tor-dev/2020-February/014146.html
- https://lists.torproject.org/pipermail/tor-dev/2020-February/014147.html
- https://security-tracker.debian.org/tracker/CVE-2020-8516
- https://trac.torproject.org/projects/tor/ticket/33129
- https://www.hackerfactor.com/blog/index.php?/archives/868-Deanonymizing-Tor-Circuits.html
