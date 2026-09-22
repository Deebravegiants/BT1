# [M] CVE-2017-0380

## Summary
Severity: Medium
Advisory: CVE-2017-0380
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-18
Source: https://osv.dev/vulnerability/CVE-2017-0380
Type: osv

## Details
The rend_service_intro_established function in or/rendservice.c in Tor before 0.2.8.15, 0.2.9.x before 0.2.9.12, 0.3.0.x before 0.3.0.11, 0.3.1.x before 0.3.1.7, and 0.3.2.x before 0.3.2.1-alpha, when SafeLogging is disabled, allows attackers to obtain sensitive information by leveraging access to the log files of a hidden service, because uninitialized stack data is included in an error message about construction of an introduction point circuit.

## References
- http://www.securitytracker.com/id/1039519
- http://www.debian.org/security/2017/dsa-3993
- https://github.com/torproject/tor/commit/09ea89764a4d3a907808ed7d4fe42abfe64bd486
- https://trac.torproject.org/projects/tor/ticket/23490
