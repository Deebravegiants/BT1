# [H] CVE-2020-10593

## Summary
Severity: High
Advisory: CVE-2020-10593
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-23
Source: https://osv.dev/vulnerability/CVE-2020-10593
Type: osv

## Details
Tor before 0.3.5.10, 0.4.x before 0.4.1.9, and 0.4.2.x before 0.4.2.7 allows remote attackers to cause a Denial of Service (memory leak), aka TROVE-2020-004. This occurs in circpad_setup_machine_on_circ because a circuit-padding machine can be negotiated twice on the same circuit.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00052.html
- https://security.gentoo.org/glsa/202003-50
- https://trac.torproject.org/projects/tor/ticket/33619
