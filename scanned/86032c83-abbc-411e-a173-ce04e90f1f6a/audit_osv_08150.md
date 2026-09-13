# [H] CVE-2016-10724

## Summary
Severity: High
Advisory: CVE-2016-10724
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2016-10724
Type: osv

## Details
Bitcoin Core before v0.13.0 allows denial of service (memory exhaustion) triggered by the remote network alert system (deprecated since Q1 2016) if an attacker can sign a message with a certain private key that had been known by unintended actors, because of an infinitely sized map. This affects other uses of the codebase, such as Bitcoin Knots before v0.13.0.knots20160814 and many altcoins.

## References
- https://bitcoin.org/en/posts/alert-key-and-vulnerabilities-disclosure
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-July/016189.html
- https://github.com/JinBean/CVE-Extension
