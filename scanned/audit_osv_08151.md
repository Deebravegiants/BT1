# [H] CVE-2016-10725

## Summary
Severity: High
Advisory: CVE-2016-10725
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2016-10725
Type: osv

## Details
In Bitcoin Core before v0.13.0, a non-final alert is able to block the special "final alert" (which is supposed to override all other alerts) because operations occur in the wrong order. This behavior occurs in the remote network alert system (deprecated since Q1 2016). This affects other uses of the codebase, such as Bitcoin Knots before v0.13.0.knots20160814 and many altcoins.

## References
- https://bitcoin.org/en/posts/alert-key-and-vulnerabilities-disclosure
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-July/016189.html
- https://github.com/JinBean/CVE-Extension
