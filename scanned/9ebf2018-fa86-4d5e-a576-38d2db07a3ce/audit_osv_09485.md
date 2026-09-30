# [H] CVE-2017-0377

## Summary
Severity: High
Advisory: CVE-2017-0377
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-02
Source: https://osv.dev/vulnerability/CVE-2017-0377
Type: osv

## Details
Tor 0.3.x before 0.3.0.9 has a guard-selection algorithm that only considers the exit relay (not the exit relay's family), which might allow remote attackers to defeat intended anonymity properties by leveraging the existence of large families.

## References
- https://blog.torproject.org/blog/tor-0309-released-security-update-clients
- https://blog.torproject.org/blog/tor-0314-alpha-released-security-update-clients
- https://security-tracker.debian.org/CVE-2017-0377
- https://trac.torproject.org/projects/tor/ticket/22753
- https://github.com/torproject/tor/commit/665baf5ed5c6186d973c46cdea165c0548027350
