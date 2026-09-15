# [C] CVE-2017-10807

## Summary
Severity: Critical
Advisory: CVE-2017-10807
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-04
Source: https://osv.dev/vulnerability/CVE-2017-10807
Type: osv

## Details
JabberD 2.x (aka jabberd2) before 2.6.1 allows anyone to authenticate using SASL ANONYMOUS, even when the sasl.anonymous c2s.xml option is not enabled.

## References
- http://www.debian.org/security/2017/dsa-3902
- http://www.securityfocus.com/bid/99511
- https://bugs.debian.org/867032
- https://github.com/jabberd2/jabberd2/commit/8416ae54ecefa670534f27a31db71d048b9c7f16
- https://github.com/jabberd2/jabberd2/releases/tag/jabberd-2.6.1
