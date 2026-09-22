# [H] CVE-2017-18225

## Summary
Severity: High
Advisory: CVE-2017-18225
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2017-18225
Type: osv

## Details
The Gentoo net-im/jabberd2 package through 2.6.1 installs jabberd, jabberd2-c2s, jabberd2-router, jabberd2-s2s, and jabberd2-sm in /usr/bin owned by the jabber account, which might allow local users to gain privileges by leveraging access to this account and then waiting for root to execute one of these programs.

## References
- https://bugs.gentoo.org/629412
