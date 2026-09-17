# [M] CVE-2022-26491

## Summary
Severity: Medium
Advisory: CVE-2022-26491
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-26491
Type: osv

## Details
An issue was discovered in Pidgin before 2.14.9. A remote attacker who can spoof DNS responses can redirect a client connection to a malicious server. The client will perform TLS certificate verification of the malicious domain name instead of the original XMPP service domain, allowing the attacker to take over control over the XMPP connection and to obtain user credentials and all communication content. This is similar to CVE-2022-24968.

## References
- https://developer.pidgin.im/wiki/FullChangeLog
- https://lists.debian.org/debian-lts-announce/2022/06/msg00005.html
- https://mail.jabber.org/pipermail/standards/2022-February/038759.html
- https://pidgin.im/about/security/advisories/cve-2022-26491/
- https://github.com/xsf/xeps/pull/1158
- https://keep.imfreedom.org/pidgin/pidgin/rev/13cdb7956bdc
